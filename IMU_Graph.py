import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- 설정 ---
SERIAL_PORT = 'COM3'  # 사용하는 시리얼 포트 이름으로 변경
BAUD_RATE = 115200    # STM32의 UART 보드레이트와 일치시켜야 함
MAX_DATA_POINTS = 100 # 그래프에 표시할 최대 데이터 포인트 수

# --- 전역 변수 ---
ser = None # 시리얼 객체

# 모든 데이터 그룹이 독립적인 deque와 x축 카운터를 갖도록 수정
# Roll
time_roll = deque(maxlen=MAX_DATA_POINTS)
accel_roll_data = deque(maxlen=MAX_DATA_POINTS)
gyro_roll_data = deque(maxlen=MAX_DATA_POINTS)
filter_roll_data = deque(maxlen=MAX_DATA_POINTS)
x_seq_roll = 0

# Pitch
time_pitch = deque(maxlen=MAX_DATA_POINTS)
accel_pitch_data = deque(maxlen=MAX_DATA_POINTS)
gyro_pitch_data = deque(maxlen=MAX_DATA_POINTS)
filter_pitch_data = deque(maxlen=MAX_DATA_POINTS)
x_seq_pitch = 0

# Yaw
time_yaw = deque(maxlen=MAX_DATA_POINTS)
yaw_data = deque(maxlen=MAX_DATA_POINTS)
x_seq_yaw = 0

# Accelerometer (Raw)
time_a = deque(maxlen=MAX_DATA_POINTS)
accel_x_data = deque(maxlen=MAX_DATA_POINTS)
accel_y_data = deque(maxlen=MAX_DATA_POINTS)
accel_z_data = deque(maxlen=MAX_DATA_POINTS)
x_seq_a = 0

# Gyroscope (Raw)
time_g = deque(maxlen=MAX_DATA_POINTS)
gyro_x_data = deque(maxlen=MAX_DATA_POINTS)
gyro_y_data = deque(maxlen=MAX_DATA_POINTS)
gyro_z_data = deque(maxlen=MAX_DATA_POINTS)
x_seq_g = 0

# Accelerometer (Filtered)
time_af = deque(maxlen=MAX_DATA_POINTS)
accelf_x_data = deque(maxlen=MAX_DATA_POINTS)
accelf_y_data = deque(maxlen=MAX_DATA_POINTS)
accelf_z_data = deque(maxlen=MAX_DATA_POINTS)
x_seq_af = 0

# Gyroscope (Filtered)
time_gf = deque(maxlen=MAX_DATA_POINTS)
gyrof_x_data = deque(maxlen=MAX_DATA_POINTS)
gyrof_y_data = deque(maxlen=MAX_DATA_POINTS)
gyrof_z_data = deque(maxlen=MAX_DATA_POINTS)
x_seq_gf = 0

# --- 각 그래프 창 생성 ---
fig_roll, ax_roll = plt.subplots()
fig_pitch, ax_pitch = plt.subplots()
fig_yaw, ax_yaw = plt.subplots()
fig_accel, ax_accel = plt.subplots()
fig_gyro, ax_gyro = plt.subplots()
fig_accel_f, ax_accel_f = plt.subplots()
fig_gyro_f, ax_gyro_f = plt.subplots()

# --- 각 그래프의 라인 초기화 ---
# Roll
line_accel_roll, = ax_roll.plot([], [], 'r-', label='Accel_roll')
line_gyro_roll, = ax_roll.plot([], [], 'g-', label='Gyro_roll')
line_filter_roll, = ax_roll.plot([], [], 'b-', label='Filter_roll')

# Pitch
line_accel_pitch, = ax_pitch.plot([], [], 'r-', label='Accel_pitch')
line_gyro_pitch, = ax_pitch.plot([], [], 'g-', label='Gyro_pitch')
line_filter_pitch, = ax_pitch.plot([], [], 'b-', label='Filter_pitch')

# Yaw
line_yaw, = ax_yaw.plot([], [], 'b-', label='Yaw')

# Accelerometer (Raw)
line_accel_x, = ax_accel.plot([], [], 'r-', label='Accel X')
line_accel_y, = ax_accel.plot([], [], 'g-', label='Accel Y')
line_accel_z, = ax_accel.plot([], [], 'b-', label='Accel Z')

# Gyroscope (Raw)
line_gyro_x, = ax_gyro.plot([], [], 'r-', label='Gyro X')
line_gyro_y, = ax_gyro.plot([], [], 'g-', label='Gyro Y')
line_gyro_z, = ax_gyro.plot([], [], 'b-', label='Gyro Z')

# Offset_Accelerometer
line_accelf_x, = ax_accel_f.plot([], [], 'r-', label='Accel_Offset X')
line_accelf_y, = ax_accel_f.plot([], [], 'g-', label='Accel_Offset Y')
line_accelf_z, = ax_accel_f.plot([], [], 'b-', label='Accel_Offset Z')

# Offset_Gyroscope
line_gyrof_x, = ax_gyro_f.plot([], [], 'r-', label='Gyro_Offset X')
line_gyrof_y, = ax_gyro_f.plot([], [], 'g-', label='Gyro_Offset Y')
line_gyrof_z, = ax_gyro_f.plot([], [], 'b-', label='Gyro_Offset Z')

# ## 변경: 새로 추가된 라인들을 all_lines 튜플에 포함
all_lines = (
    line_accel_roll, line_gyro_roll, line_filter_roll,
    line_accel_pitch, line_gyro_pitch, line_filter_pitch,
    line_yaw,
    line_accel_x, line_accel_y, line_accel_z,
    line_gyro_x, line_gyro_y, line_gyro_z,
    line_accelf_x, line_accelf_y, line_accelf_z,
    line_gyrof_x, line_gyrof_y, line_gyrof_z
)

def init_plot():
    """그래프 초기 설정"""
    # ... (init_plot 내용은 이전과 동일하게 유지해도 되므로 생략) ...
    # Roll 그래프 설정
    ax_roll.set_title('Roll Data')
    ax_roll.set_ylabel('Degrees')
    ax_roll.set_ylim(-180, 180)
    ax_roll.legend(loc='upper left')
    ax_roll.grid(True)

    # Pitch 그래프 설정
    ax_pitch.set_title('Pitch Data')
    ax_pitch.set_ylabel('Degrees')
    ax_pitch.set_ylim(-180, 180)
    ax_pitch.legend(loc='upper left')
    ax_pitch.grid(True)

    # Yaw 그래프 설정
    ax_yaw.set_title('Yaw Data')
    ax_yaw.set_ylabel('Degrees')
    ax_yaw.set_ylim(-180, 180)
    ax_yaw.legend(loc='upper left')
    ax_yaw.grid(True)

    # Accelerometer 그래프 설정
    ax_accel.set_title('Accelerometer Data')
    ax_accel.set_ylabel('g')
    ax_accel.set_ylim(-4, 4)
    ax_accel.legend(loc='upper left')
    ax_accel.grid(True)

    # Gyroscope 그래프 설정
    ax_gyro.set_title('Gyroscope Data')
    ax_gyro.set_ylabel('dps')
    ax_gyro.set_xlabel('Time Sequence')
    ax_gyro.set_ylim(-500, 500)
    ax_gyro.legend(loc='upper left')
    ax_gyro.grid(True)

    # Offset_Accelerometer 그래프 설정
    ax_accel_f.set_title('Offset_Accelerometer Data')
    ax_accel_f.set_ylabel('g')
    ax_accel_f.set_ylim(-4, 4)
    ax_accel_f.legend(loc='upper left')
    ax_accel_f.grid(True)

    # Offset_Gyroscope 그래프 설정
    ax_gyro_f.set_title('Offset_Gyroscope Data')
    ax_gyro_f.set_ylabel('dps')
    ax_gyro_f.set_xlabel('Time Sequence')
    ax_gyro_f.set_ylim(-500, 500)
    ax_gyro_f.legend(loc='upper left')
    ax_gyro_f.grid(True)

    # 각 창 레이아웃 조정
    for fig in [fig_roll, fig_pitch, fig_yaw, fig_accel, fig_gyro, fig_accel_f, fig_gyro_f]:
        fig.tight_layout()

    return all_lines

def read_serial_data():
    """시리얼 데이터를 읽고 파싱하는 함수"""
    # 각 데이터에 맞는 전역 변수를 사용하도록 수정
    global x_seq_roll, x_seq_pitch, x_seq_yaw, x_seq_a, x_seq_g, x_seq_af, x_seq_gf
    try:
        while ser and ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received: {line}")
            values = line.split(',')
            
            try:
                if len(values) == 4:
                    prefix, v1, v2, v3 = values[0], float(values[1]), float(values[2]), float(values[3])
                    
                    if prefix == 'roll':
                        time_roll.append(x_seq_roll)
                        accel_roll_data.append(v1)
                        gyro_roll_data.append(v2)
                        filter_roll_data.append(v3)
                        x_seq_roll += 1
                    elif prefix == 'pitch':
                        time_pitch.append(x_seq_pitch)
                        accel_pitch_data.append(v1)
                        gyro_pitch_data.append(v2)
                        filter_pitch_data.append(v3)
                        x_seq_pitch += 1
                    elif prefix == 'a':
                        time_a.append(x_seq_a)
                        accel_x_data.append(v1)
                        accel_y_data.append(v2)
                        accel_z_data.append(v3)
                        x_seq_a += 1
                    elif prefix == 'g':
                        time_g.append(x_seq_g)
                        gyro_x_data.append(v1)
                        gyro_y_data.append(v2)
                        gyro_z_data.append(v3)
                        x_seq_g += 1
                    elif prefix == 'af':
                        time_af.append(x_seq_af)
                        accelf_x_data.append(v1)
                        accelf_y_data.append(v2)
                        accelf_z_data.append(v3)
                        x_seq_af += 1
                    elif prefix == 'gf':
                        time_gf.append(x_seq_gf)
                        gyrof_x_data.append(v1)
                        gyrof_y_data.append(v2)
                        gyrof_z_data.append(v3)
                        x_seq_gf += 1
                
                elif len(values) == 2:
                    prefix, v1 = values[0], float(values[1])
                    if prefix == 'yaw':
                        time_yaw.append(x_seq_yaw)
                        yaw_data.append(v1)
                        x_seq_yaw += 1

            except (ValueError, IndexError):
                # 데이터 파싱 에러 또는 형식 불일치: 무시
                print(f"데이터 파싱 에러 또는 형식 불일치: {line}")
                pass

    except serial.SerialException as e:
        print(f"시리얼 에러: {e}")
        pass


def update(frame):
    """실시간으로 그래프를 업데이트하는 함수"""
    read_serial_data()

    # 모든 그래프가 자신만의 (시간, 데이터) 쌍을 사용하도록 수정
    line_accel_roll.set_data(time_roll, accel_roll_data)
    line_gyro_roll.set_data(time_roll, gyro_roll_data)
    line_filter_roll.set_data(time_roll, filter_roll_data)
    
    line_accel_pitch.set_data(time_pitch, accel_pitch_data)
    line_gyro_pitch.set_data(time_pitch, gyro_pitch_data)
    line_filter_pitch.set_data(time_pitch, filter_pitch_data)
    
    line_yaw.set_data(time_yaw, yaw_data)

    line_accel_x.set_data(time_a, accel_x_data)
    line_accel_y.set_data(time_a, accel_y_data)
    line_accel_z.set_data(time_a, accel_z_data)

    line_gyro_x.set_data(time_g, gyro_x_data)
    line_gyro_y.set_data(time_g, gyro_y_data)
    line_gyro_z.set_data(time_g, gyro_z_data)

    line_accelf_x.set_data(time_af, accelf_x_data)
    line_accelf_y.set_data(time_af, accelf_y_data)
    line_accelf_z.set_data(time_af, accelf_z_data)

    line_gyrof_x.set_data(time_gf, gyrof_x_data)
    line_gyrof_y.set_data(time_gf, gyrof_y_data)
    line_gyrof_z.set_data(time_gf, gyrof_z_data)

    # 각 축의 범위를 동적으로 업데이트
    all_axes = [
        (ax_roll, time_roll), (ax_pitch, time_pitch), (ax_yaw, time_yaw),
        (ax_accel, time_a), (ax_gyro, time_g),
        (ax_accel_f, time_af), (ax_gyro_f, time_gf)
    ]
    for ax, time_data in all_axes:
        if time_data:
            ax.set_xlim(min(time_data), max(time_data) + 1)
        ax.relim()
        ax.autoscale_view(scalex=False, scaley=True)

    return all_lines

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print(f"{SERIAL_PORT} 포트가 성공적으로 열렸습니다.")
        
        ani = animation.FuncAnimation(
            fig_roll, update, init_func=init_plot, blit=True,
            interval=20, cache_frame_data=False
        )
        
        plt.show()

    except serial.SerialException as e:
        print(f"에러: {SERIAL_PORT} 포트를 열 수 없습니다. 포트 이름을 확인하거나 다른 프로그램에서 사용 중인지 확인하세요.")
        print(e)
        
    finally:
        if ser and ser.is_open:
            ser.close()
            print(f"\n{SERIAL_PORT} 포트를 닫았습니다.")
