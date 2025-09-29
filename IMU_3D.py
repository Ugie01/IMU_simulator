import serial
import math
from vpython import *

# --- 설정 ---
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

# --- 전역 변수 ---
running = True # 프로그램 실행 상태를 제어하는 플래그

# --- 함수 정의 ---
def stop_program():
    """종료 버튼을 누르면 호출되어 running 플래그를 False로 바꾼다."""
    global running
    running = False
    print("종료 버튼 클릭. 프로그램을 종료합니다.")

# --- VPython 3D Scene 설정 ---
scene.width = 800; scene.height = 600; scene.background = color.gray(0.95)
scene.title = "IMU 3D Visualizer (Bug Fixed)"

# --- 하단 UI (캡션, 텍스트, 버튼) 설정 ---

# 1. 고정 설명 텍스트를 먼저 설정
scene.caption = "World Axes -> X: Red, Y: Green, Z: Blue\nIMU Axes -> X: Orange, Y: Magenta, Z: Cyan\n"

# 2. Roll, Pitch, Yaw 값을 표시할 'wtext' 위젯 추가 (이 부분의 텍스트가 계속 바뀜)
data_wtext = wtext(text='Roll: 0.00\nPitch: 0.00\nYaw: 0.00\n\n')

# 3. 마지막으로 버튼 생성
button(bind=stop_program, text='프로그램 종료')

# --- 3D 객체 설정 ---
# 3D 공간에 있던 기존 label은 삭제함
arrow(pos=vector(0,0,0), axis=vector(10,0,0), color=color.red, shaftwidth=0.2)
arrow(pos=vector(0,0,0), axis=vector(0,10,0), color=color.green, shaftwidth=0.2)
arrow(pos=vector(0,0,0), axis=vector(0,0,10), color=color.blue, shaftwidth=0.2)

arrow_length = 5
imu_x_axis = arrow(pos=vector(0,0,0), axis=vector(arrow_length,0,0), color=color.orange, shaftwidth=0.3)
imu_y_axis = arrow(pos=vector(0,0,0), axis=vector(0,arrow_length,0), color=color.magenta, shaftwidth=0.3)
imu_z_axis = arrow(pos=vector(0,0,0), axis=vector(0,0,arrow_length), color=color.cyan, shaftwidth=0.3)

# --- 시리얼 통신 설정 ---
ser = None # ser 변수를 미리 선언
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"{SERIAL_PORT} 포트가 성공적으로 열렸습니다.")
except serial.SerialException as e:
    print(f"에러: {SERIAL_PORT} 포트를 열 수 없습니다. 시리얼 포트를 확인하세요.")
    running = False # 시리얼 포트가 열리지 않으면 바로 종료

# --- 메인 루프 ---
while running:
    try:
        if ser and ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            parts = line.split(',')
            if len(parts) == 4:
                prefix, roll_deg, pitch_deg, yaw_deg = (parts[0], float(parts[1]), float(parts[2]), float(parts[3]))
                if prefix == 'c':
                    print(f"Received: {parts}")  # 수신된 데이터 출력 (디버깅용)
                    # wtext 위젯의 텍스트 업데이트
                    data_wtext.text = f"Roll: {roll_deg:.2f}\nPitch: {pitch_deg:.2f}\nYaw: {yaw_deg:.2f}\n\n"

                    roll_rad = math.radians(roll_deg)
                    pitch_rad = math.radians(pitch_deg)
                    yaw_rad = math.radians(yaw_deg)

                    imu_x = vector(1, 0, 0)
                    imu_y = vector(0, 1, 0)
                    imu_z = vector(0, 0, 1)

                    world_x = vector(1, 0, 0)
                    world_y = vector(0, 1, 0)
                    world_z = vector(0, 0, 1)

                    imu_x = imu_x.rotate(angle=roll_rad, axis=world_x)
                    imu_y = imu_y.rotate(angle=roll_rad, axis=world_x)
                    imu_z = imu_z.rotate(angle=roll_rad, axis=world_x)

                    imu_x = imu_x.rotate(angle=pitch_rad, axis=world_y)
                    imu_y = imu_y.rotate(angle=pitch_rad, axis=world_y)
                    imu_z = imu_z.rotate(angle=pitch_rad, axis=world_y)

                    imu_x = imu_x.rotate(angle=yaw_rad, axis=world_z)
                    imu_y = imu_y.rotate(angle=yaw_rad, axis=world_z)
                    imu_z = imu_z.rotate(angle=yaw_rad, axis=world_z)

                    imu_x_axis.axis = imu_x * arrow_length
                    imu_y_axis.axis = imu_y * arrow_length
                    imu_z_axis.axis = imu_z * arrow_length

    except (ValueError, IndexError):
        pass
    except KeyboardInterrupt:
        print("프로그램 종료 (Ctrl+C).")
        running = False
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        running = False

# --- 프로그램 종료 시 자원 정리 ---
if ser and ser.is_open:
    ser.close()
    print(f"{SERIAL_PORT} 포트를 닫았습니다.")
