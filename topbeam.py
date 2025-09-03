#============ Percobaan dengan setting TopBeam =============
import serial
import csv
import time
import numpy as np

def analyze_vehicle(profile_data):
    # Konversi ke numpy array
    data = np.array(profile_data, dtype=np.float64)
    print(profile_data)

    # Normalisasi (0-1)
    data_norm = (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-9)

    # Fitur utama
    avg_height = np.mean(data_norm)        # tinggi rata-rata
    print("Tinggi rata-rata : ")
    print(avg_height)
    std_height = np.std(data_norm)         # variasi tinggi
    print("Variasi tinggi : ")
    print(std_height)
    peaks = np.sum((data_norm[1:-1] > data_norm[:-2]) & (data_norm[1:-1] > data_norm[2:]))  # jumlah puncak
    #print(peaks)

    # Aturan sederhana (threshold bisa disesuaikan dengan data nyata)
    if avg_height > 0.6 and std_height < 0.4 and peaks <= 2:
        return "Bus\n"
    else:
        return "Truk\n"

# === Konfigurasi Serial ===
# Sesuaikan port dan baudrate dengan perangkatmu
ser = serial.Serial('COM5', 19200, timeout=1)
time.sleep(2)  # tunggu koneksi stabil

#Connect
data = bytes([0x1B, 0x1B, 0x0D, 0x0A, 0x53, 0x41, 0x56, 0x45, 0x0D, 0x0A, 0x52, 0x45, 0x50, 0x4F, 0x52, 0x54, 0x3F, 0x0D, 0x0A, 0x4D, 0x4F, 0x44, 0x45, 0x3F, 0x0D, 0x0A, 0x4E, 0x42, 0x45, 0x41, 0x4D, 0x53, 0x3F, 0x0D, 0x0A, 0x53, 0x59, 0x4E, 0x0D, 0x0A])
ser.write(data)
print("Kirim perintah start scan")

# Nama file output
filename = "data_serial.csv"
flag = False
arr = []

# Buka file CSV untuk menulis data
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Tulis header kolom
    writer.writerow(["Data"])
    
    print("Mulai membaca data serial... Tekan CTRL+C untuk berhenti.")
    try:
        while True:
            if ser.in_waiting > 0:
                raw = ser.read_until(b'\r')  # baca sampai CR (0x0D)

                if raw.startswith(b'\x21\x0D'):
                    payload = raw[2:-1]  # buang header (0x21 0x0D) & CR                    
                else:
                    if raw.startswith(b'>\x01'):
                        # buang SOH (0x01) dan CR (0x0D)
                        data = raw[1:].decode('ascii', errors='ignore').strip()
                        print("Data inisialisasi : ", data)
                    else:
                        data = raw.decode('ascii', errors='ignore').strip()
                        dec_value = int(data, 16)
                        #print(dec_value)

                        if dec_value != 0:                
                            # Simpan ke excel
                            writer.writerow([dec_value])
                            #print(f"{data}")
                            dec_value = int(data, 16)
                            arr.append(dec_value)
                            flag = True
                        else:
                            if flag:
                                #print(arr)
                                print("Profil diklasifikasikan sebagai:", analyze_vehicle(arr))
                                flag = False
                                arr.clear()
                    

    except KeyboardInterrupt:        
        data = bytes([0x1B, 0x1B, 0x0D, 0x0A])
        ser.write(data)
        print("Kirim perintah stop scan")
        ser.close()
        print("Program Exit")
#======= Percobaan Top Beam ======================================================
