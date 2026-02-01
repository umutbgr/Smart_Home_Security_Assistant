#Yüz verisinin kaydedilmesini istediğiniz kişinin 30 kere yüzünün fotoğrafını çeker.
import cv2
import os
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') # type: ignore

DATA_PATH = 'yuz_tanima'

person_name = input("İsminizi girin: ")
person_dir = os.path.join(DATA_PATH, person_name)

# --- Düzeltilen Kısım ---

# 1. Ana veri klasörünü oluştur: DATA_PATH (yuz_tanima)
# exist_ok=True kullanarak klasör zaten varsa hata vermesini engelle.
try:
    os.makedirs(DATA_PATH, exist_ok=True)
    # print(f"'{DATA_PATH}' klasörü hazırlandı/mevcut.") # İsteğe bağlı
except Exception as e:
    print(f"Hata oluştu: {e}")
    exit()

# 2. Kişinin klasörünü oluştur: person_dir (yuz_tanima/aleyna)
if not os.path.exists(person_dir):
    os.makedirs(person_dir)
    print(f"'{person_name}' Klasörü oluşturuldu.")
else:
    print(f"'{person_name}' Klasörü zaten mevcut.")

cap = cv2.VideoCapture(0)
count = 0
MAX_IMAGES = 30

print(f"\n{MAX_IMAGES} adet yüz görüntüsü yakalanacak. Lütfen kameraya bakınız.")

while count < MAX_IMAGES:
    ret, frame = cap.read()
    if not ret:
        print("Kamera okunamadı.")
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor = 1.1, 
        minNeighbors = 5,
        minSize = (30, 30)

    )

    for(x,y,w,h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        face_crop = gray[y:y+h, x:x+w]

        image_name = os.path.join(person_dir, f'{person_name}_{count:02d}.jpg')

        cv2.imwrite(image_name, face_crop)#yüz görüntüsünü kaydetme
        count += 1
        print(f"Görüntü yakalandı: {count}/{MAX_IMAGES}")

        if count >= MAX_IMAGES:
            break

        cv2.imshow('Yuz Toplama', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):#q tuşuna basılırsa çık
            break

cap.release()
cv2.destroyAllWindows()
print("\n Veri toplama tamamlandı.")
