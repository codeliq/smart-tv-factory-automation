<template>
  <div class="dashboard-container">
    <SummaryBot :logs="logs" />
    <main class="grid-layout">
      <!-- 좌측 상단: Dobot 사진 + 카메라 -->
      <div class="dobot-photo">
        <img src="/dobot.jpg" alt="Dobot Photo" class="dobot-img" />
      </div>
      <div class="camera-stream">
        <h3>📷 카메라 실시간 송출</h3>
        <!-- 카메라 컴포넌트 자리 -->
        <CameraStream />
      </div>

      <!-- 우측 상단: 보드 요약 + 현재 상태 -->
      <div class="board-summary">
        <BoardStats :total="board.total" :blue="board.blue" :white="board.white" :red="board.red" />
      </div>
      <div class="current-status">
        <h3>🛠️ 현재 동작 상태</h3>
        <p><strong>🕒:</strong> {{ status.timestamp }}</p>
        <p><strong>📶:</strong> {{ status.signal }}</p>
        <p><strong>⚙️:</strong> {{ status.currentJob }}</p>
      </div>

      <!-- 중단: 최근 작업 스택 -->
      <div class="task-stack">
        <TaskStackBadge :taskStack="taskStack" />
      </div>

      <!-- 하단 좌측: 관절각도 (2x2) -->
      <div class="arm-angle-chart">
        <ArmAngleChart :angles="angles" />
      </div>

      <!-- 하단 가운데: 현재 위치 (가로 크기 축소) -->
      <div class="position-map">
        <PositionMap :position="position" />
      </div>

      <!-- 하단 우측: 최근 작업 이력 -->
      <div class="log-list-box">
        <h3>📜 최근 작업 이력</h3>
        <ul class="log-list">
          <li v-for="(log, index) in logs" :key="index">
            <span class="log-time">🕒 {{ log.time }}</span>
            <span class="log-desc">{{ log.desc }}</span>
          </li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script>
import ArmAngleChart from "@/components/charts/ArmAngleChart.vue";
import PositionMap from "@/components/charts/PositionMap.vue";
import BoardStats from "@/components/BoardStats.vue";
import TaskStackBadge from '@/components/charts/TaskStackBadge.vue';
import CameraStream from '@/components/CameraStream.vue'
import SummaryBot from '@/components/ai/SummaryBot.vue';

export default {
  name: "Dashboard",
  components: {
    ArmAngleChart,
    PositionMap,
    BoardStats,
    TaskStackBadge,
    CameraStream,
    SummaryBot,
  },
  data() {
    return {
      angles: [],
      taskStack: [],
      currentTask: null,
      taskStartTime: null,
      position: { x: 0, y: 0, z: 0 },
      board: { total: 0, blue: 0, white: 0, red: 0 },
      status: {
        timestamp: new Date().toLocaleTimeString(),
        signal: 2,
        currentJob: "프레임 장착 중",
      },
      logs: []
    };
  },
  mounted() {
    console.log("[Dashboard mounted]");
    setInterval(() => {
      this.status.timestamp = new Date().toLocaleTimeString();
    }, 1000);

    const socket = new WebSocket("ws://localhost:3001");
   socket.onmessage = (event) => {
  const data = JSON.parse(event.data);

  this.angles = data.angles;
  this.position = data.position;

  this.status = {
    timestamp: new Date().toLocaleTimeString(),
    signal: data.signal,
    currentJob: data.currentJob
  };

  // ✅ 보드 수 실시간 업데이트
  const recognizedColor = data.recognized?.color;
  if (recognizedColor === 'blue') this.board.blue += 1;
  else if (recognizedColor === 'white') this.board.white += 1;
  else if (recognizedColor === 'red') this.board.red += 1;

  this.board.total = this.board.blue + this.board.white + this.board.red;

  // ✅ 작업 스택 누적
  const now = performance.now();
  if (this.currentTask && this.taskStartTime && this.currentTask !== data.currentJob) {
    const duration = (now - this.taskStartTime) / 1000;
    this.taskStack.unshift({
      task: this.currentTask,
      time: parseFloat(duration.toFixed(2))
    });
    if (this.taskStack.length > 5) this.taskStack.pop();
  }
  this.currentTask = data.currentJob;
  this.taskStartTime = now;

  // ✅ 로그 출력
  const defective = data.recognized?.defective ? "❌ 불량" : "✔️ 정상";
  this.logs.unshift({
    time: new Date().toLocaleTimeString(),
    desc: `${recognizedColor} 보드 - ${defective}`
  });
  if (this.logs.length > 10) this.logs.pop();
};

  }
};
</script>

<style scoped>
.dashboard-container {
  background: #f0f9ff;
  min-height: 100vh;
}

.navbar {
  background: linear-gradient(to right, #3b82f6, #6366f1);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.logo .icon {
  font-size: 1.8rem;
  margin-right: 0.5rem;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 1.5rem;
}

.nav-links li a {
  color: #e0f2fe;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
  font-size: 1rem;
}

.nav-links li a:hover {
  color: #ffffff;
}

.grid-layout {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto auto auto;
  gap: 1rem;
  padding: 1rem;
}

.dobot-photo, .camera-stream, .board-summary, .current-status, .task-stack,
.arm-angle-chart, .position-map, .log-list-box {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.dobot-photo { grid-column: 1 / 2; grid-row: 1 / 2; }
.camera-stream { grid-column: 2 / 3; grid-row: 1 / 2; }
.board-summary { grid-column: 3 / 4; grid-row: 1 / 2; }
.current-status { grid-column: 4 / 5; grid-row: 1 / 2; }
.task-stack { grid-column: 1 / 5; grid-row: 2 / 3; }
.arm-angle-chart { grid-column: 1 / 2; grid-row: 3 / 4; }
.position-map { grid-column: 2 / 4; grid-row: 3 / 4; }
.log-list-box { grid-column: 4 / 5; grid-row: 3 / 4; }

.dobot-img {
  width: 100%;
  height: auto;
  border-radius: 8px;
}

.log-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.log-list li {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.5rem 0;
  color: #374151;
}

.log-time {
  font-weight: 600;
  color: #1f2937;
}

.log-desc {
  color: #4b5563;
}
</style>
