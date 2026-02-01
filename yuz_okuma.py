# -*- coding: utf-8 -*-
import numpy as np
import pickle
import cv2
import dlib
from scipy.spatial import distance # Vektörler arası mesafeyi hesaplamak için
import time
import firebase_admin
from firebase_admin import credentials, db


son_komut_zamani = 0 #Arduinoyu her karede yorma diye.
komut_araligi = 3 #3 snde bir sinyal gönder
son_hirsiz_durumu = 0  # 0 = guvenli, 1 = hirsiz

# --- Dlib ve Model Yolları ---
# Dikkat: Bu dosyaların hepsi aynı klasörde olmalıdır.
FACE_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
FACE_RECOGNITION_PATH = "dlib_face_recognition_resnet_model_v1.dat"
RECOGNIZER_PATH = "recognizer.pkl"
LABEL_ENCODER_PATH = "le.pkl"

# --- Modelleri Yükle ---
try:
    # Dlib Modelleri
    predictor = dlib.shape_predictor(FACE_PREDICTOR_PATH)
    face_recognizer = dlib.face_recognition_model_v1(FACE_RECOGNITION_PATH)
    detector = dlib.get_frontal_face_detector()

    # Eğitilmiş SVM Sınıflandırıcı ve Etiket Kodlayıcı
    with open(RECOGNIZER_PATH, "rb") as f:
        recognizer = pickle.load(f)
    with open(LABEL_ENCODER_PATH, "rb") as f:
        le = pickle.load(f)
    
    print("[BILGI] Tüm modeller başarıyla yüklendi.")

except FileNotFoundError:
    print("\n[HATA] Gerekli dosyalardan biri bulunamadı.")
    print("Lütfen 'shape_predictor_68_face_landmarks.dat', 'dlib_face_recognition_resnet_model_v1.dat', 'recognizer.pkl' ve 'le.pkl' dosyalarının bu betikle AYNI KLASÖRDE olduğundan emin olun.")
    exit()
except Exception as e:
    print(f"[HATA] Model yüklenirken bir hata oluştu: {e}")
    exit()

cred = credentials.Certificate(
    "firebase-key.json"
)
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://PROJE_ADINIZ.firebaseio.com/"
})

firebase_ref = db.reference("/")
print("[BILGI] Firebase baglantisi kuruldu.")


# --- OpenCV Kamera Başlatma ---
cap = cv2.VideoCapture(0) # 0 varsayılan web kamerasını temsil eder

if not cap.isOpened():
    print("[HATA] Kamera açılamadı. Lütfen kamera bağlantısını kontrol edin veya doğru kamera dizinini (0, 1, vb.) kullanın.")
    exit()

print("\n[BILGI] Kameradan görüntü alınıyor. Çıkmak için 'q' tuşuna basın.")

while True:
    # 1. Kameradan kare (frame) al
    ret, frame = cap.read()
    if not ret:
        print("[HATA] Kare alınamıyor.")
        break
        
    # Görüntü kalitesini artırmak için yeniden boyutlandırma (isteğe bağlı)
    frame = cv2.resize(frame, (0, 0), fx=0.7, fy=0.7)

    # Dlib'in RGB formatında çalışması daha yaygındır
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 2. Yüzleri tespit et
    # 1 parametresi, görüntüyü 1 kez yukarı örnekle (upsample) demektir, bu da küçük yüzleri bulmaya yardımcı olur.
    rects = detector(rgb, 1)

    # 3. Her tespit edilen yüz üzerinde döngü yap
    for rect in rects:
        # 3.1. Yüzün kilit noktalarını (landmarks) bul
        shape = predictor(rgb, rect)
        
        # 3.2. Yüz gömme vektörünü (embedding) hesapla (128-D vektör)
        face_descriptor = face_recognizer.compute_face_descriptor(rgb, shape)
        new_embedding = np.array(face_descriptor, dtype="float64")
        
        # Sınıflandırıcıya vermeden önce boyutu ayarla
        new_embedding = new_embedding.reshape(1, -1)

        # 3.3. Eğitilmiş SVM ile tahmin yap
        # predict_proba, her bir sınıfa ait olma olasılığını verir
        preds = recognizer.predict_proba(new_embedding)[0]
        
        # En yüksek olasılığa sahip sınıfı ve olasılık değerini bul
        j = np.argmax(preds)
        proba = preds[j]
        
        # Olasılığı isim etiketine çevir
        name = le.classes_[j]
        simdi = time.time()

        proba = preds[j]
        name = le.classes_[j]
        simdi = time.time()

        # Eğer güven oranı %85 üzerindeyse ve üzerinden 3 saniye geçmişse
       # --- GÜNCEL VE ÇALIŞAN KARAR MEKANİZMASI ---
        # Eğer güven oranı %85 üzerindeyse ve üzerinden 3 saniye geçmişse
        if proba * 100 > 85 and (simdi - son_komut_zamani > komut_araligi):
            # Durum kontrolünü (if son_hirsiz_durumu != 0) test için kaldırdık
            firebase_ref.update({
                "hirsiz": 0
            })
            print(f"[FIREBASE] Güvenli yüz Hoşgeldin : {name} | Skor: {proba*100:.2f}")
            son_hirsiz_durumu = 0
            son_komut_zamani = simdi
        
        # Eğer hırsız durumu (%40 altı) ise
        elif proba * 100 < 60 and (simdi - son_komut_zamani > komut_araligi):
            firebase_ref.update({
                "hirsiz": 1
            })
            print("[FIREBASE] HIRSIZ ALGILANDI!")
            son_hirsiz_durumu = 1
            son_komut_zamani = simdi
        # --- EKRAN ÇIKTISI OLUŞTURMA ---
        
        # 3.4. Yüzün etrafına kare çiz
        x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
        
        # Güvenilirlik %70'in üzerindeyse yeşil, altındaysa kırmızı çiz
        color = (0, 255, 0) if proba * 100 > 70 else (0, 0, 255) # BGR formatı
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # 3.5. İsim ve yüzde bilgisini kare üzerine yaz
        text = f"{name}: {proba*100:.2f}%"
        
        # Metin arka planı için kare
        cv2.rectangle(frame, (x1, y1 - 35), (x2, y1), color, -1) 
        
        # Metin
        cv2.putText(frame, text, (x1 + 6, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)


    # 4. Görüntü penceresini göster
    cv2.imshow("Gercek Zamanli Yuz Tanima", frame)

    # 'q' tuşuna basılırsa döngüyü kır
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Kaynakları Serbest Bırak ---
cap.release()
cv2.destroyAllWindows()

print("[TAMAM] Yüz tanıma sonlandırıldı.")
