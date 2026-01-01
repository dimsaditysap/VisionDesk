import cv2
import mediapipe as mp
import time
import math


# Inisialisasi Modul MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0)

# --- VARIABEL GLOBAL PENYUSUNAN KALIMAT ---
current_sentence = ""
last_char = ""
last_char_start_time = 0
HOLD_THRESHOLD = 1.0  # Durasi tunda (detik) untuk konfirmasi input
SPACE_THRESHOLD = 2.0 # Durasi tunda (detik) untuk spasi

def calculate_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def get_fingers_status(hand_landmarks, handedness_label):
    """
    Mengembalikan status jari [Ibu jari, Telunjuk, Tengah, Manis, Kelingking].
    True = Terbuka, False = Tertutup.
    """
    landmarks = hand_landmarks.landmark
    fingers = []
    
    # --- IBU JARI (THUMB) ---
    # Analisis posisi ibu jari relatif terhadap telapak tangan.
    # Deteksi status menekuk (tucked) berdasarkan kedekatan ujung ibu jari dengan pangkal kelingking (Pinky MCP).
    
    thumb_tip = landmarks[4]
    thumb_mcp = landmarks[2]
    pinky_mcp = landmarks[17]
    
    # Menghitung jarak Euclidean referensi
    dist_thumb_pinky = math.sqrt((thumb_tip.x - pinky_mcp.x)**2 + (thumb_tip.y - pinky_mcp.y)**2)
    dist_thumb_mcp = math.sqrt((thumb_tip.x - thumb_mcp.x)**2 + (thumb_tip.y - thumb_mcp.y)**2)
    
    # Skala referensi berdasarkan panjang jari telunjuk
    scale_ref = math.sqrt((landmarks[8].x - landmarks[5].x)**2 + (landmarks[8].y - landmarks[5].y)**2)
    
    # Penentuan status tertutup berdasarkan ambang batas rasio jarak
    if dist_thumb_pinky < (1.3 * scale_ref): 
        # Ibu jari mendekati area kelingking
        is_thumb_open = False
    elif dist_thumb_mcp < (1.0 * scale_ref):
        # Ibu jari tertekuk pada posisi pangkal
        is_thumb_open = False
    else:
        # Ibu jari terentang menjauhi telapak
        is_thumb_open = True
        
    fingers.append(is_thumb_open)
    
    # --- OTHERS ---
    # [8, 6], [12, 10], [16, 14], [20, 18]
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        fingers.append(landmarks[tip].y < landmarks[pip].y)
        
    return fingers

def recognize_gesture(fingers, landmarks, handedness_label):
    """
    Identifikasi gestur berdasarkan kombinasi jari yang terbuka.
    Gestur yang dikenali: HAI, SIP/OKE, I LOVE YOU, dan Angka 1-3.
    """
    # Indeks jari
    THUMB, INDEX, MIDDLE, RING, PINKY = 0, 1, 2, 3, 4
    
    # Menghitung jumlah jari yang terbuka
    up_count = fingers.count(True)
    
    # --- DEFINISI GESTUR ---
    
    # 1. HAI / DADAH
    # Terpenuhi jika mayoritas jari (4 atau lebih) terbuka.
    if up_count >= 4:
        return "HAI"
    
    # 2. I LOVE YOU (Ibu Jari, Telunjuk, Kelingking)
    # Toleransi diberikan pada ibu jari untuk mengakomodasi variasi "Rock".
    if fingers[INDEX] and fingers[PINKY] and not fingers[MIDDLE] and not fingers[RING]:
        return "I LOVE YOU"

    # 3. SIP / OKE (Hanya Ibu Jari)
    if fingers[THUMB] and not fingers[INDEX] and not fingers[MIDDLE] and not fingers[RING] and not fingers[PINKY]:
        # Validasi vertikal: Ujung ibu jari harus berada di atas pangkal telunjuk.
        thumb_tip = landmarks[4]
        index_mcp = landmarks[5]
        if thumb_tip.y < (index_mcp.y - 0.02):
            return "SIP/OKE"
        else:
            return "" 

    # 4. ANGKA 1-3
    
    # Angka 1 (Telunjuk)
    if fingers[INDEX] and not fingers[MIDDLE] and not fingers[RING] and not fingers[PINKY] and not fingers[THUMB]:
        return "1"
    
    # Angka 2 (Telunjuk + Tengah)
    if fingers[INDEX] and fingers[MIDDLE] and not fingers[RING] and not fingers[PINKY] and not fingers[THUMB]:
        return "2"
        
    # Angka 3 (Telunjuk + Tengah + Manis)
    if fingers[INDEX] and fingers[MIDDLE] and fingers[RING] and not fingers[PINKY] and not fingers[THUMB]:
        return "3"
        
    return "" # Undefined

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5) as hands:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        detected_char = ""
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness = results.multi_handedness[idx].classification[0].label
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
                # Logic
                fingers = get_fingers_status(hand_landmarks, handedness)
                detected_char = recognize_gesture(fingers, hand_landmarks.landmark, handedness)
        
        # --- LOGIKA PENYUSUNAN KALIMAT ---
        curr_time = time.time()
        
        if detected_char:
            if detected_char == last_char:
                duration = curr_time - last_char_start_time
                
                # Penentuan durasi ambang batas
                target_duration = SPACE_THRESHOLD if detected_char == " " else HOLD_THRESHOLD
                
                # Indikator Visual: Progress Bar
                progress = min(duration / target_duration, 1.0)
                bar_width = int(progress * 200)
                cv2.rectangle(image, (50, 400), (50 + bar_width, 420), (0, 255, 0), -1)
                cv2.rectangle(image, (50, 400), (250, 420), (255, 255, 255), 2)
                
                if duration > target_duration:
                    # Validasi karakter/kata untuk ditambahkan
                    if detected_char == " ":
                        current_sentence += " "
                    elif len(detected_char) == 1:
                        current_sentence += detected_char
                    else:
                        # Penambahan kata dengan spasi otomatis
                        if not current_sentence.endswith(" "):
                            current_sentence += " "
                        current_sentence += detected_char + " "
                    
                    # Reset timer untuk mencegah duplikasi input
                    last_char_start_time = curr_time + 0.5 
            else:
                # Perubahan gestur terdeteksi
                last_char = detected_char
                last_char_start_time = curr_time
        else:
            # Tidak ada gestur valid
            last_char = ""
            last_char_start_time = curr_time

        # --- UI DISPLAY ---
        h, w, _ = image.shape
        
        # 1. Area Tampilan Gestur Terdeteksi
        cv2.rectangle(image, (0, 0), (w, 80), (20, 20, 20), -1)
        cv2.putText(image, f"Terdeteksi: {detected_char}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # 2. Area Tampilan Kalimat (Bawah)
        cv2.rectangle(image, (0, h-60), (w, h), (240, 240, 240), -1)
        cv2.putText(image, f"Kalimat: {current_sentence}", (20, h-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (10, 10, 10), 2)
        
        # Panduan Pengguna Singkat
        cv2.putText(image, "Tahan 1 detik untuk mengetik.", (w-400, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow('SignTalk Pro - Sentence Builder', image)
        
        if cv2.waitKey(5) & 0xFF == 27:
            break
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
