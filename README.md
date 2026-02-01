# 🏠 Entegre Akıllı Ev Sistemi

Bu proje; **gerçek zamanlı yüz tanıma**, **NLP tabanlı sesli komut algılama** ve **bulut tabanlı veri senkronizasyonu** teknolojilerini bir araya getiren, modüler ve ölçeklenebilir bir **akıllı ev çözümüdür**.

Sistem; kullanıcıyı yüzünden tanıyabilir, sesli komutları doğal dilde anlayabilir ve tüm ev senaryolarını **Firebase Realtime Database** üzerinden anlık olarak yönetir. Amaç; minimum etkileşimle maksimum konfor ve güvenlik sağlamaktır.

---

## 🎯 Projenin Amacı

* Ev içi otomasyon senaryolarını tek merkezden yönetmek
* Yetkisiz girişleri yüz tanıma ile tespit etmek
* Sesli komutlarla doğal ve hızlı kontrol sağlamak
* Tüm sistem durumlarını bulut üzerinden senkronize etmek

---

## 🏠 Akıllı Ev Modları ve Senaryolar

Sistem, farklı kullanım senaryoları için önceden tanımlanmış modlar içerir:

### 🎬 Sinema Modu

* **Tetikleme:** Sesli komut → *"Sinema modunu aç"*
* **Davranış:**

  * Firebase üzerinde ilgili değer `1` olarak güncellenir
  * Işıklar kısılır, ortam aydınlatması ayarlanır
  * Medya sistemleri sinema senaryosuna geçer

---

### 🛡️ Güvenlik (Hırsız) Modu

* **Tetikleme:** Yüz tanıma modülü
* **Davranış:**

  * Tanımlı olmayan bir yüz **düşük güvenilirlik** ile algılandığında
  * Firebase üzerindeki `hirsiz` bayrağı aktif edilir
  * Güvenlik senaryoları (alarm, bildirim vb.) devreye alınabilir

---

### 🏡 Ev Modu

* **Tetikleme:**

  * Kullanıcının eve giriş yapması
  * Manuel sesli komut
* **Davranış:**

  * Sistem varsayılan ve dengeli çalışma ayarlarına döner
  * Günlük kullanım için optimize edilmiş senaryo aktif olur

---

## 🚀 Teknik Özellikler

### 👁️ Yüz Tanıma Mimarisi

* **Kütüphaneler:** Dlib, OpenCV
* **Model:** ResNet tabanlı yüz tanıma
* **Doğruluk:** %85+ kimlik doğrulama başarımı

---

### 🎙️ Sesli Etkileşim ve NLP

* **Ses Tanıma:** Google Speech Recognition
* **Sesli Geri Bildirim:** gTTS + pygame
* **Özellikler:**

  * Doğal dilde komut algılama
  * Anlık sesli yanıt üretimi

---

### ☁️ Bulut Entegrasyonu

* **Altyapı:** Firebase Realtime Database
* **Fonksiyon:**

  * Tüm modların ve sensör durumlarının anlık senkronizasyonu
  * Donanım ve yazılım bileşenleri arasında veri köprüsü

---

### 🧩 Modüler Mimari

Sistem aşağıdaki bağımsız modüllerden oluşur:

* Yüz eğitimi ve tanıma
* Sesli komut algılama
* Firebase veri yönetimi
* Ana asistan kontrol döngüsü

Bu yapı sayesinde sistem kolayca genişletilebilir ve bakım yapılabilir.

---

## 🛠️ Kurulum ve Gereksinimler

Gerekli Python kütüphanelerini yüklemek için:

```bash
pip install opencv-python dlib numpy firebase-admin SpeechRecognition gTTS pygame scipy
```

> **Not:** `dlib` kurulumu için sisteminizde **CMake** yüklü olmalıdır.

---

## 🔑 Eksik Dosyaların Tamamlanması

Güvenlik ve dosya boyutu nedeniyle bazı kritik dosyalar repoya dahil edilmemiştir. Projeyi çalıştırabilmek için aşağıdaki dosyaları eklemelisiniz:

### 🔐 Firebase Credentials

* `.json` uzantılı **Firebase servis hesabı anahtarı**
* Ana dizine yerleştirilmelidir

---

### 🧠 Dlib Modelleri

Aşağıdaki dosyaları indirip proje dizinine ekleyin:

* `shape_predictor_68_face_landmarks.dat`
* `dlib_face_recognition_resnet_model_v1.dat`

---

### 👤 Kişisel Yüz Modelleri

* `yuz_egitme.py` ile kendi yüz verinizi toplayın
* Eğitim sonrası oluşan `.pkl` dosyalarını kullanın

---

## 👥 Ekip ve Katkılar

Bu proje ekip çalışmasıyla geliştirilmiştir:

* **Umut Buğra Şahin:**

  * Proje mimarisi
  * Görüntü işleme tabanlı güvenlik sistemi
  * Firebase entegrasyonu
  * Ana asistan yapısı

* **Proje Ekibi:**

  * Modların senaryolarının mantıksal kurgusu
  * Test ve doğrulama süreçleri

---

## 📄 Lisans

MIT License © 2026 – **Umut Buğra Şahin**

Bu proje eğitim ve geliştirme amaçlıdır. Dilediğiniz gibi kullanabilir ve geliştirebilirsiniz.

## ℹ️ Dipnot ve Açıklama

Bu repoda bazı modüller, senaryo dosyaları veya yapılandırma bileşenleri bilinçli olarak paylaşılmamıştır.

Bunun nedeni:

 - İlgili kısımların ekip arkadaşları tarafından geliştirilmiş olması,

 - Ortak çalışma kapsamında bu bileşenlerin ayrı depolarda veya özel repositorilerde tutulması,

Fikri mülkiyet ve ekip içi paylaşım sınırlarına saygı gösterilmesidir.

## Bu dokümanda bahsi geçen tüm modlar sistem mimarisinde yer almakta olup, bu repoda bulunan kodlar projenin:

 - Ana kontrol yapısını,

 - Yüz tanıma tabanlı güvenlik mimarisini,

 - Firebase entegrasyonunu,

 - Sesli asistan altyapısını

temsil etmektedir.

