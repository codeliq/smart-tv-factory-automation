import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import socket
import threading
import time

from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from dobot_msgs.action import PointToPoint
from dobot_msgs.srv import SuctionCupControl

HOST = '192.168.110.117'
CONVEYOR_PORT = 65432
ROBODK_PORT = 20000

# ------------------ Pick-and-Place Class ------------------
class PanelPickAndPlace:
    def __init__(self, node: Node):
        self.node = node
        self.action_client = ActionClient(
            node, PointToPoint, 'PTP_action', callback_group=ReentrantCallbackGroup()
        )
        self.suction_client = node.create_client(SuctionCupControl, 'dobot_suction_cup_service')
        while not self.suction_client.wait_for_service(timeout_sec=3.0):
            node.get_logger().info('Suction service not available, waiting...')
        self.srv_req = SuctionCupControl.Request()
        self.tasks = self.generate_tasks()
        self.task_idx = 0

    #224/-33.4/-3.2   / 167.5/-35.8/2.5
    def generate_tasks(self):
        panels = [
            [128.7, 144.7 , 167.5, -35.8],
            [54.9, 203.0, 167.5, -35.8],
            [90.0, 141.5, 227.0, -33.2],
            [93.8, 206.0, 167.5, -35.8],
            
        ]
        tasks = []
        for p in panels:
            px, py, pz, pl = p
            tasks += [
                ('move', [px, py, 60.0, 0.0], 1),
                ('move', [px, py, -65.0, 0.0], 1),
                ('gripper', True),
                ('move', [px, py, 60.0, 0.0], 1),
                ('move', [pz, pl, 50.0, 0.0], 1),
                ('move', [pz, pl, -3.5, 0.0], 1),
                ('gripper', False),
                ('move', [pz, pl, 50.0, 0.0], 1),
                ('move', [px, py, 60.0, 0.0], 1)
            ]
        return tasks

    def execute_next(self):
        if self.task_idx >= len(self.tasks):
            self.node.get_logger().info('All pick-and-place tasks completed.')
            return
        task = self.tasks[self.task_idx]
        self.node.get_logger().info(f'Executing PNP task {self.task_idx}: {task[0]}')
        if task[0] == 'gripper':
            self._call_suction(task[1])
        else:
            _, target, mtype = task
            self._send_ptp_goal(target, mtype)
        self.task_idx += 1

    def _after_task(self):
        # Pause at end of each panel batch (9 tasks) until RoboDK signal
        if self.task_idx % 9 == 0:
            panel_no = (self.task_idx // 9)
            self.node.get_logger().info(
                f'Completed panel batch {panel_no}, waiting for RoboDK signal'
            )
        else:
            self.execute_next()
    def _call_suction(self, enable):
        self.srv_req.enable_suction = enable
        fut = self.suction_client.call_async(self.srv_req)
        fut.add_done_callback(lambda f: (
            self.node.get_logger().info(f'Suction set to {enable}'),
            self._after_task()
        ))

    def _send_ptp_goal(self, target, motion_type):
        goal = PointToPoint.Goal()
        goal.target_pose = target
        goal.motion_type = motion_type
        self.action_client.wait_for_server()
        send_fut = self.action_client.send_goal_async(goal)
        send_fut.add_done_callback(self._response)

    def _response(self, future):
        gh = future.result()
        if not gh.accepted:
            self.node.get_logger().warn('PTP goal rejected')
            return
        res_fut = gh.get_result_async()
        res_fut.add_done_callback(lambda f: (
            self.node.get_logger().info('PTP move done'),
            self._after_task()
        ))

    def _feedback(self, fb):
        self.node.get_logger().info(f'PTP feedback: {fb.feedback}')

# ------------------ Unified Node ------------------
class UnifiedNode(Node):
    def __init__(self):
        super().__init__('unified_node')
        # Initialize connection attributes
        self.conv_conn = None
        self.rd_conn = None
        self.conv_ready = False
        self.rd_ready = False
        self.initial_started = False
        self.last_triggered = {}
        self.last_detection_time = 0   # <-- 추가!
        self.cooltime = 7              # <-- 쿨타임(초) 설정!
        # Detection subscriber
        self.sub = self.create_subscription(
            String, '/detection_results', self._detection_cb, 10
        )

        # Conveyor server thread
        threading.Thread(
            target=self._start_conveyor_server, daemon=True
        ).start()

        # RoboDK server thread
        threading.Thread(
            target=self._start_robodk_server, daemon=True
        ).start()

        # Pick-and-place manager
        self.pp = PanelPickAndPlace(self)

    def _check_start(self):
        if self.conv_ready and self.rd_ready and not self.initial_started:
            self.initial_started = True
            self.get_logger().info(
                'Both clients connected, starting first pick-and-place sequence'
            )
            self.pp.execute_next()

    def _start_conveyor_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, CONVEYOR_PORT)); s.listen()
        self.get_logger().info(f'Conveyor server listening on {HOST}:{CONVEYOR_PORT}')
        conn, addr = s.accept(); self.conv_conn = conn
        self.get_logger().info(f'Conveyor client connected: {addr}')
        self.conv_ready = True
        self._check_start()

    def _start_robodk_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, ROBODK_PORT)); s.listen()
        self.get_logger().info(f'RoboDK server listening on {HOST}:{ROBODK_PORT}')
        conn, addr = s.accept(); self.rd_conn = conn
        self.get_logger().info(f'RoboDK client connected: {addr}')
        self.rd_ready = True
        self._check_start()

        while True:
            try:
                self.get_logger().info('Waiting for RoboDK message...')
                raw = conn.recv(1024)
                self.get_logger().info(f'Raw recv bytes: {raw!r}')
                if not raw:
                    self.get_logger().info('No data received, retrying...')
                    continue
                msg = raw.decode(errors='ignore').strip()
                self.get_logger().info(f'Decoded message: "{msg}"')

                if msg.startswith('wait_sig'):
                    self.get_logger().info(
                        f'Received RoboDK signal: {msg}, executing next PNP task'
                    )
                    self.pp.execute_next()
                else:
                    self.get_logger().info(f'Ignored RoboDK message: "{msg}"')
            except Exception as e:
                self.get_logger().error(f'Error in RoboDK recv loop: {e}')
                break

    def _detection_cb(self, msg: String):
        data = msg.data.strip().lower().split()
        if len(data) != 2:
            return
        label, color = data; key = (label, color)

        # 빨간색이면 conveyor에만 신호, 7초 대기 후 pnp 다음 태스크로
        if color == 'red':
            if self.last_triggered.get(label, None) == color:
                return
            self.last_triggered[label] = color

            code = 'R'
            if self.conv_conn:
                self.conv_conn.sendall(code.encode())
                self.get_logger().info(f'Sent code {code} to conveyor')

                # 7초 뒤에 pnp(로봇) 넘기기 (스레드로 지연)
                threading.Timer(7.0, self.pp.execute_next).start()
            return

        # 나머지는 쿨타임 및 중복 방지
        now = time.time()
        if now - self.last_detection_time < self.cooltime:
            return
        self.last_detection_time = now

        if color == 'unknown':
            self.last_triggered[label] = None
            return
        if self.last_triggered.get(label, None) == color:
            return
        self.last_triggered[label] = color

        job, code = None, None
        if label == 'back_panel' and color == 'white': job='1'; code='B'
        elif label == 'board_panel' and color == 'white': job='2'; code='B'
        elif color == 'blue': job='3'; code='B'
        # elif color == 'red': code='R'   # red는 위에서 이미 처리

        if job and self.rd_conn:
            self.rd_conn.sendall(job.encode())
            self.get_logger().info(f'Sent job {job}')
        if code:
            self.conv_conn.sendall(code.encode())
            self.get_logger().info(f'Sent code {code} to conveyor')
        if job is None:
            self.pp.execute_next()


# ------------------ Main ------------------
def main(args=None):
    rclpy.init(args=args)
    node = UnifiedNode()
    try:
        rclpy.spin(node, executor=MultiThreadedExecutor())
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__=='__main__':
    main()
