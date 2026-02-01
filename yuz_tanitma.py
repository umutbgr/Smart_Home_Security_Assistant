# -*- coding: utf-8 -*-
import numpy as np
import pickle
import cv2
import dlib
import os
from imutils import paths
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import sys # Programı hata durumunda kapatmak için

# --- DOSYA VE MODEL YOLLARI ---
FACE_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
FACE_RECOGNITION_PATH = "dlib_face_recognition_resnet_model_v1.dat"
DATA_PATH = 'yuz_tanima'
EMBEDDING_DATA_PATH = "yuz_tanima_verisi.npy"

# --- 1. ÖZELLİK ÇIKARMA (EMBEDDING EXTRACTION) ---
def extract_embeddings():
    """Veri setindeki resimlerden 128 boyutlu yüz özelliklerini çıkarır ve kaydeder."""
    global known_embeddings, known_names
    
    try:
        # Yüz tanıma modellerini başlat
        predictor = dlib.shape_predictor(FACE_PREDICTOR_PATH)
        face_recognizer = dlib.face_recognition_model_v1(FACE_RECOGNITION_PATH)
        detector = dlib.get_frontal_face_detector()
    except Exception as e:
        print(f"[HATA] Dlib Model Dosyaları Yüklenemedi: {e}")
        print("Lütfen .dat uzantılı model dosyalarının bu betikle aynı klasörde olduğundan emin olun.")
        sys.exit(1) # Programı kapat

    known_embeddings = []
    known_names = []

    print("\n[BILGI] Görüntüleri işliyor ve gömmeleri (embeddings) çıkarıyor...")
    imagePaths = list(paths.list_images(DATA_PATH))
    
    if len(imagePaths) == 0:
        print(f"[HATA] '{DATA_PATH}' klasöründe hiç resim bulunamadı. Lütfen klasör yapısını kontrol edin.")
        sys.exit(1)

    # Her bir görüntü yolu üzerinde döngü
    for (i, imagePath) in enumerate(imagePaths):
        name = imagePath.split(os.path.sep)[-2]

        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # type: ignore
        
        print(f"[{i+1}/{len(imagePaths)}] İşleniyor: {name}")

        rects = detector(rgb, 1)

        if len(rects) > 0:
            rect = rects[0]
            shape = predictor(rgb, rect)
            face_embedding = np.array(face_recognizer.compute_face_descriptor(rgb, shape))
            
            known_embeddings.append(face_embedding)
            known_names.append(name)
        else:
            print(f"[UYARI] {name} görüntüsünde yüz algılanamadı, atlanıyor.")

    # Sonuçları NumPy Dosyası Olarak Kaydetme
    data = {"embeddings": known_embeddings, "names": known_names}
    np.save(EMBEDDING_DATA_PATH, data)

    print(f"\n[TAMAM] Tüm gömmeler başarıyla çıkarıldı ve '{EMBEDDING_DATA_PATH}' dosyasına kaydedildi!")


# --- 2. MODEL EĞİTİMİ (SVM CLASSIFIER) ---
def train_model():
    """Çıkarılan gömmeleri kullanarak bir SVM sınıflandırıcısı eğitir ve kaydeder."""
    
    print("\n[BILGI] Oluşturulan gömmeler diske yükleniyor ve model eğitiliyor...")
    
    # Kaydedilen Veriyi Diskten Yükle
    try:
        data = np.load(EMBEDDING_DATA_PATH, allow_pickle=True).item()
        known_embeddings = data["embeddings"]
        known_names = data["names"]
    except FileNotFoundError:
        print(f"[HATA] '{EMBEDDING_DATA_PATH}' dosyası bulunamadı. Önce özellik çıkarma adımını çalıştırın.")
        sys.exit(1)

    # 🚨 Hata Çözümü: Veri Seti Kontrolü ve Boyutlandırma
    if len(known_embeddings) == 0:
        print("[HATA] Veri setinde hiç geçerli yüz (embedding) bulunamadı. Lütfen resimlerinizi kontrol edin.")
        sys.exit(1)
        
    known_embeddings = np.array(known_embeddings) # 2D diziye dönüştür

    # Etiketleri Sayısallaştır (Label Encoding)
    print("[BILGI] Etiketler kodlanıyor...")
    le = LabelEncoder()
    labels = le.fit_transform(known_names)

    # MODEL EĞİTİMİ (SVM)
    print("[BILGI] Sınıflandırıcı (SVM) eğitiliyor...")
    recognizer = SVC(kernel="linear", probability=True)
    recognizer.fit(known_embeddings, labels)

    # EĞİTİLMİŞ MODELİ KAYDETME
    print("[BILGI] Eğitilmiş modeller diske kaydediliyor...")
    with open("recognizer.pkl", "wb") as f:
        f.write(pickle.dumps(recognizer))
    with open("le.pkl", "wb") as f:
        f.write(pickle.dumps(le))

    print("\n[SONUÇ] Eğitim tamamlandı. 'recognizer.pkl' ve 'le.pkl' dosyaları oluşturuldu!")


# --- 3. GERÇEK ZAMANLI TANIMA (WEBCAM) ---
def start_recognition():
    """Webcam'den anlık görüntü alarak yüz tanıma yapar."""
    
    print("\n[BILGI] Gerçek zamanlı tanıma başlatılıyor...")

    try:
        # Modelleri Yükle (Eğitim sonrası oluşanlar)
        predictor = dlib.shape_predictor(FACE_PREDICTOR_PATH)
        face_recognizer = dlib.face_recognition_model_v1(FACE_RECOGNITION_PATH)
        detector = dlib.get_frontal_face_detector()
        
        with open("recognizer.pkl", "rb") as f:
            recognizer = pickle.load(f)
        with open("le.pkl", "rb") as f:
            le = pickle.load(f)
        
        print("[BILGI] Tanıma modelleri başarıyla yüklendi. Kamera açılıyor...")

    except FileNotFoundError:
        print("[HATA] Tanıma için gerekli .pkl dosyaları bulunamadı. Lütfen önce eğitim (train_model) adımını çalıştırın.")
        sys.exit(1)
    except Exception as e:
        print(f"[HATA] Model yüklenirken bir sorun oluştu: {e}")
        sys.exit(1)


    # OpenCV Kamera Başlatma
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[HATA] Kamera açılamadı. Kamera bağlantısını kontrol edin.")
        sys.exit(1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rects = detector(rgb, 1)

        for rect in rects:
            shape = predictor(rgb, rect)
            face_descriptor = face_recognizer.compute_face_descriptor(rgb, shape)
            new_embedding = np.array(face_descriptor, dtype="float64").reshape(1, -1)

            # Tahmin yap
            preds = recognizer.predict_proba(new_embedding)[0]
            j = np.argmax(preds)
            proba = preds[j]
            name = le.classes_[j]
            
            # Sonuçları çiz
            x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
            color = (0, 255, 0) if proba * 100 > 70 else (0, 0, 255) # Yeşil veya Kırmızı
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            text = f"{name}: {proba*100:.2f}%"
            cv2.rectangle(frame, (x1, y1 - 35), (x2, y1), color, -1) 
            cv2.putText(frame, text, (x1 + 6, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        cv2.imshow("Gercek Zamanli Yuz Tanima", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Kaynakları Serbest Bırak
    cap.release()
    cv2.destroyAllWindows()
    print("[TAMAM] Yüz tanıma sonlandırıldı.")


# --- ANA ÇALIŞTIRMA KISMI ---
if __name__ == "__main__":
    
    # 1. ÖZELLİK ÇIKARMA
    extract_embeddings()
    
    # 2. MODEL EĞİTİMİ
    train_model()
    
    # 3. GERÇEK ZAMANLI TANIMA
    start_recognition()