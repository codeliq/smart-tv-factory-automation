# rp5_client.py  (Raspberry Pi)
import socket
import time
import RPi.GPIO as GPIO

HOST = '192.168.110.117'
PORT = 65432

def connect_to_server():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            print(f"[RPi] Connected to {HOST}:{PORT}")
            return s
        except socket.error as e:
            print(f"[RPi] Connection failed: {e}, retrying in 5s")
            time.sleep(5)

def main():
    GPIO.setmode(GPIO.BCM)
    SERVO_PIN   = 18
    STEPPER_PIN = 27
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    GPIO.setup(STEPPER_PIN, GPIO.OUT)
    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start((135/18.0)+2.5)  # 기본 135°

    s = connect_to_server()
    try:
        while True:
            data = s.recv(1024)
            if not data:
                break
            cmd = data.decode().strip()
            print(f"[RPi] Received '{cmd}'")
            if cmd == 'R':
                pwm.ChangeDutyCycle((95/18.0)+2.5)
            elif cmd == 'B':
                pwm.ChangeDutyCycle((175/18.0)+2.5)
            elif cmd == 'C':
                pwm.ChangeDutyCycle((135/18.0)+2.5)
            elif cmd == 'S':
                GPIO.output(STEPPER_PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(STEPPER_PIN, GPIO.LOW)
            else:
                print(f"[RPi] Unknown cmd '{cmd}'")
    except KeyboardInterrupt:
        pass
    finally:
        pwm.stop()
        GPIO.cleanup()
        s.close()
        print("[RPi] Shutdown cleanly")

if __name__ == '__main__':
    main()
