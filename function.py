import numpy as np
import random

# ฟังก์ชันสำหรับจำลองการแพร่กระจายของไฟ
def spread_fire(forest, moisture_level, wind_direction, wind_strength, temperature, step, unburned_list, burning_list, ash_list):
    grid_size = forest.shape[0]  # ขนาดของตาราง
    new_forest = forest.copy()  # สร้างสำเนาของป่าปัจจุบัน
    
    # กำหนดอิทธิพลของลมตามทิศทางของลม เพื่อส่งผลต่อการแพร่กระจายของไฟ
    wind_bias = {
        "N": {(-1, 0): 1.5, (-1, -1): 1.3, (-1, 1): 1.3, (1, 0): 0.3, (1, -1): 0.5, (1, 1): 0.5},
        "S": {(1, 0): 1.5, (1, -1): 1.3, (1, 1): 1.3, (-1, 0): 0.3, (-1, -1): 0.5, (-1, 1): 0.5},
        "E": {(0, 1): 1.5, (-1, 1): 1.3, (1, 1): 1.3, (0, -1): 0.3, (-1, -1): 0.5, (1, -1): 0.5},
        "W": {(0, -1): 1.5, (-1, -1): 1.3, (1, -1): 1.3, (0, 1): 0.3, (-1, 1): 0.5, (1, 1): 0.5}
    }
    
    # คำนวณอัตราการแพร่ของไฟตามอุณหภูมิ
    temperature_factor = 0.1 * (temperature - 10) / 10  # จะเพิ่มโอกาสการแพร่กระจายตามอุณหภูมิที่สูงกว่า 10 องศา (เป็นค่าประมาณ)
    
    # วนลูปผ่านตารางเพื่อตรวจสอบเซลล์ที่ไฟกำลังลุกไหม้และแพร่กระจายไปยังเซลล์ที่ไม่ไหม้
    for i in range(grid_size):
        for j in range(grid_size):
            if forest[i, j] == 2:  # ถ้าเซลล์นี้มีไฟลุกไหม้
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # ทิศทาง 4 ทิศทางในการแพร่กระจายไฟ
                for di, dj in directions:
                    ni, nj = i + di, j + dj  # คำนวณตำแหน่งเซลล์ใหม่
                    if 0 <= ni < grid_size and 0 <= nj < grid_size:  # ตรวจสอบว่าเซลล์ใหม่อยู่ภายในขอบเขตของตาราง
                        if forest[ni, nj] == 1:  # ถ้าเซลล์นั้นยังไม่ถูกไฟไหม้ (ค่า 1)
                            spread_chance = (1.0 - moisture_level) + temperature_factor  # คำนวณโอกาสการแพร่กระจายจากความชื้นและอุณหภูมิ
                            # ปรับอัตราการแพร่กระจายตามทิศทางลมและความแรงของลม
                            if wind_direction in wind_bias and (di, dj) in wind_bias[wind_direction]:
                                spread_chance *= wind_bias[wind_direction][(di, dj)] * wind_strength
                            if random.random() < spread_chance:  # ใช้โอกาสสุ่มในการแพร่กระจายไฟ
                                new_forest[ni, nj] = 2  # ทำให้เซลล์ใหม่ลุกไหม้
                new_forest[i, j] = 3  # เซลล์ที่ถูกไฟไหม้กลายเป็นเถ้าถ่าน (ค่า 3)

    # ติดตามตำแหน่งของเซลล์ที่ยังไม่ไหม้, กำลังไหม้, และเถ้าถ่านในแต่ละขั้นตอน
    unburned = np.argwhere(new_forest == 1)
    burning = np.argwhere(new_forest == 2)
    ash = np.argwhere(new_forest == 3)

    # เพิ่มสถานะปัจจุบันของแต่ละประเภทลงในรายการ
    unburned_list.append(unburned)
    burning_list.append(burning)
    ash_list.append(ash)

    return new_forest


# ฟังก์ชันสำหรับจำลองไฟในป่าผ่านหลาย ๆ ขั้นตอน
def simulate_fire(grid_size, moisture, iterations, wind_direction="N", wind_strength=1.0, temperature=30):
    moisture_level = moisture / 100  # แปลงค่าความชื้นเป็นค่าระหว่าง 0 ถึง 1
    steps = iterations
    
    forest = np.ones((grid_size, grid_size))  # สร้างป่าด้วยเซลล์ที่ยังไม่ถูกไฟไหม้ทั้งหมด (ค่า 1)
    
    # เลือกจุดเริ่มต้นของไฟแบบสุ่ม
    fire_start = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
    forest[fire_start] = 2  # ทำให้เซลล์จุดเริ่มต้นของไฟลุกไหม้ (ค่า 2)
    
    # เก็บผลลัพธ์ของแต่ละขั้นตอนของการจำลอง
    results = np.zeros((steps + 1, grid_size, grid_size))
    results[0] = forest.copy()  # สถานะเริ่มต้นของป่า
    
    # รายการสำหรับเก็บสถานะของเซลล์ที่ยังไม่ไหม้, กำลังไหม้ และเถ้าถ่านในแต่ละขั้นตอน
    unburned_list = []
    burning_list = []
    ash_list = []

    # รันการจำลองไฟไปตามจำนวนขั้นตอนที่กำหนด
    for t in range(1, steps + 1):
        forest = spread_fire(forest, moisture_level, wind_direction, wind_strength, temperature, t, unburned_list, burning_list, ash_list)
        results[t] = forest.copy()  # เก็บสถานะหลังจากการแพร่กระจายในแต่ละขั้นตอน
    
    return results, unburned_list, burning_list, ash_list

# ฟังก์ชันเพื่อดึงข้อมูลสถิติจากการจำลองไฟ
def get_fire_stats(unburned_list, burning_list, ash_list):
    num_steps = len(unburned_list)  # จำนวนขั้นตอนในการจำลอง
    # นับจำนวนเซลล์ในแต่ละประเภทในแต่ละขั้นตอน
    unburned_counts = [len(unburned) for unburned in unburned_list]
    burning_counts = [len(burning) for burning in burning_list]
    ash_counts = [len(ash) for ash in ash_list]
    
    return unburned_counts, burning_counts, ash_counts
