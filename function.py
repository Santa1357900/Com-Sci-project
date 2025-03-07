import numpy as np
import random

# ฟังก์ชันสำหรับจำลองการแพร่กระจายของไฟ (ใช้ Monte Carlo)
def spread_fire(forest, moisture_level, wind_direction, wind_strength, temperature, step, unburned_list, burning_list, ash_list):
    grid_size = forest.shape[0]  # กำหนดขนาดของตารางป่า
    new_forest = forest.copy()  # คัดลอกตารางป่าเพื่อแก้ไข
    trials = 100

    # กำหนดค่า bias ของลมในแต่ละทิศทาง
    wind_bias = {
        "N": {(-1, 0): 1.5, (-1, -1): 1.3, (-1, 1): 1.3, (1, 0): 0.3, (1, -1): 0.5, (1, 1): 0.5},
        "S": {(1, 0): 1.5, (1, -1): 1.3, (1, 1): 1.3, (-1, 0): 0.3, (-1, -1): 0.5, (-1, 1): 0.5},
        "E": {(0, 1): 1.5, (-1, 1): 1.3, (1, 1): 1.3, (0, -1): 0.3, (-1, -1): 0.5, (1, -1): 0.5},
        "W": {(0, -1): 1.5, (-1, -1): 1.3, (1, -1): 1.3, (0, 1): 0.3, (-1, 1): 0.5, (1, 1): 0.5}
    }
    
    # ปัจจัยจากอุณหภูมิที่มีผลต่อการลุกลามของไฟ
    temperature_factor = 0.1 * (temperature - 10) / 10

    # วนลูปในแต่ละจุดของตารางป่า
    for i in range(grid_size):
        for j in range(grid_size):
            if forest[i, j] == 2:  # ถ้าเซลล์นั้นกำลังลุกไหม้ (ค่า 2)
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # ทิศทางการลุกลาม
                for di, dj in directions:
                    ni, nj = i + di, j + dj  # คำนวณตำแหน่งใหม่
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:
                        if forest[ni, nj] == 1:  # ถ้าเซลล์นั้นยังไม่ลุกไหม้ (ค่า 1)
                            spread_chance = (1.0 - moisture_level) + temperature_factor  # โอกาสในการลุกลาม
                            # เพิ่มโอกาสตามทิศทางและความแรงของลม
                            if wind_direction in wind_bias and (di, dj) in wind_bias[wind_direction]:
                                spread_chance *= wind_bias[wind_direction][(di, dj)] * wind_strength
                            
                            # ใช้ Monte Carlo เพื่อสุ่มหลายครั้งและหาค่าเฉลี่ย
                            success_count = 0
                            for _ in range(trials):
                                if random.random() < spread_chance:  # สุ่มดูว่าจะลุกลามหรือไม่
                                    success_count += 1
                            
                            # ถ้าเฉลี่ยผลลัพธ์สำเร็จมากกว่าครึ่งหนึ่ง ให้ถือว่าไฟลุกลาม
                            if success_count / trials > 0.5:
                                new_forest[ni, nj] = 2  # ลุกลามไปเซลล์นั้น
                new_forest[i, j] = 3  # เซลล์ที่ลุกไหม้จะกลายเป็นขี้เถ้า (ค่า 3)

    # บันทึกสถานะของป่าในแต่ละช่วงเวลา
    unburned = np.argwhere(new_forest == 1)
    burning = np.argwhere(new_forest == 2)
    ash = np.argwhere(new_forest == 3)

    unburned_list.append((step, unburned))
    burning_list.append((step, burning))
    ash_list.append((step, ash))

    return new_forest  # คืนค่าตารางป่าใหม่


# ฟังก์ชันสำหรับจำลองไฟในป่าผ่านหลาย ๆ ขั้นตอน (รองรับหลายจุดเริ่มต้น)
def simulate_fire(grid_size, moisture, steps, wind_direction="N", wind_strength=1.0, temperature=30, fire_starts=None):
    moisture_level = moisture / 100  # แปลงความชื้นเป็นค่า 0-1
    forest = np.ones((grid_size, grid_size))  # สร้างตารางป่าที่มีค่าเป็น 1 (ยังไม่ลุกไหม้)
    
    # ตรวจสอบจุดเริ่มต้นของไฟ
    if fire_starts is None:
        fire_starts = [(random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))]  # จุดเริ่มต้นสุ่มถ้าไม่ระบุ
    
    if isinstance(fire_starts, tuple):
        fire_starts = [fire_starts]  # แปลง tuple เป็นลิสต์

    # ตรวจสอบว่าแต่ละจุดอยู่ในขอบเขตของตารางหรือไม่
    for fire_start in fire_starts:
        if not (0 <= fire_start[0] < grid_size and 0 <= fire_start[1] < grid_size):
            raise ValueError("ตำแหน่งเริ่มต้นของไฟอยู่นอกขอบเขตของตาราง!")
        forest[fire_start] = 2  # กำหนดให้จุดเริ่มต้นลุกไหม้ (ค่า 2)
    
    results = np.zeros((steps + 1, grid_size, grid_size))  # สร้างตารางเก็บผลลัพธ์
    results[0] = forest.copy()  # เก็บสถานะเริ่มต้น

    unburned_list = []
    burning_list = []
    ash_list = []

    # วนลูปจำลองการลุกลามของไฟตามจำนวนขั้นตอน
    for t in range(1, steps + 1):
        forest = spread_fire(forest, moisture_level, wind_direction, wind_strength, temperature, t, unburned_list, burning_list, ash_list)
        results[t] = forest.copy()
    
    return results, unburned_list, burning_list, ash_list  # คืนค่าผลลัพธ์และข้อมูลสถิติ

def get_fire_stats(unburned_list, burning_list, ash_list):
    num_steps = len(unburned_list)
    # นับจำนวนเซลล์ที่ยังไม่ลุกไหม้, กำลังลุกไหม้, และเป็นขี้เถ้า
    unburned_counts = [len(unburned[1]) for unburned in unburned_list]
    burning_counts = [len(burning[1]) for burning in burning_list]
    ash_counts = [len(ash[1]) for ash in ash_list]
    
    return unburned_counts, burning_counts, ash_counts  # คืนค่าสถิติ


# เรียกใช้งาน โดยกำหนดจุดเริ่มต้นของไฟหลายจุด
fire_start_positions = [(5, 5), (15, 15), (25, 25)]  # กำหนดหลายจุดเริ่มต้น
results, unburned_list, burning_list, ash_list = simulate_fire(30, 40, 30, 'W', 1, 45, fire_starts=fire_start_positions)
unburned_counts, burning_counts, ash_counts =  get_fire_stats(unburned_list, burning_list, ash_list)
