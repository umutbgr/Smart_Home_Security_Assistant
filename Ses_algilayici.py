# Bu dosya, sesli komutları algılayarak Firebase üzerinden ev modlarını kontrol eder.
import speech_recognition as sr
from gtts import gTTS
import os
import pygame
import time
import firebase_admin
from firebase_admin import credentials, db

# --- Firebase Ayarları ---
if not firebase_admin._apps:
    cred = credentials.Certificate("BURAYA_FIREBASE_JSON_DOSYA_ADINI_GIRIN.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://BURAYA_FIREBASE_VERITABANI_LINKINI_GIRIN.firebaseio.com/'
    })

firebase_ref = db.reference("/")

def seslendir(metin):
    """Asistanın sesli cevap vermesini sağlar."""
    try:
        tts = gTTS(text=metin, lang='tr')
        tts.save("cevap.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("cevap.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        os.remove("cevap.mp3")
    except Exception as e:
        print(f"Seslendirme hatası: {e}")

def asistan():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nDinliyorum... (Örn: 'Sinema modunu aç' veya 'Sinema modunu kapat')")
        r.adjust_for_ambient_noise(source, duration=1) # Gürültü ayarı
        audio = r.listen(source)

    try:
        # Sesi metne çevir
        komut = r.recognize_google(audio, language='tr-TR').lower()
        print(f"Söylenen: {komut}")

        # Mantıksal Kontroller
        if "sinema modu" in komut:
            if "aç" in komut:
                firebase_ref.update({"sinemaModu": 1})
                print("[FIREBASE] sinemaModu -> 1")
                seslendir("Sinema modu açılıyor, iyi seyirler.")
            
            elif "kapat" in komut:
                firebase_ref.update({"sinemaModu": 0})
                print("[FIREBASE] sinemaModu -> 0")
                seslendir("Sinema modu kapatıldı.")
        elif "ev" in komut:
            if "aç" in komut:
                firebase_ref.update({"ev" : 1})
                print("Ev modu aktif")
                seslendir("Ev modu aktif.")
            elif "kapat"in komut:
                firebase_ref.update({"ev" : 0})
                print("Ev modu kapalı")
                seslendir("Ev modu kapalı.")
            
            else:
                print("Seslendirmenizi anlamadım.")

    except sr.UnknownValueError:
        # Ses anlaşılamazsa sessiz kal
        pass
    except sr.RequestError:
        print("İnternet bağlantısı sorunu yaşanıyor.")

if __name__ == "__main__":
    print("Asistan Başlatıldı...")
    while True:

        asistan()
