# 🌐 FlaskileForum (ctrl_shift_n)

FlaskileForum, Python'ın esnek web framework'ü **Flask** kullanılarak geliştirilmiş, modern ve dinamik bir forum platformudur. İsmini ve konseptini tarayıcıların gizli sekme kısayolundan (`ctrl_shift_n`) alan bu proje; kullanıcıların güvenli bir şekilde hesap oluşturup fikirlerini paylaştığı, başlıklar açıp tartışmalara katıldığı dinamik bir backend mimarisine sahiptir.

---

## ✨ Özellikler

* **Kullanıcı Kimlik Doğrulama (Auth):** Güvenli kayıt olma, giriş yapma ve çıkış işlemlerini içeren üyelik sistemi.
* **Şifre Güvenliği:** Kullanıcı şifreleri veritabanında ham metin olarak değil, `Werkzeug` kriptografik hashleme algoritmaları ile güvenli bir şekilde saklanır.
* **Dinamik Gönderi (Post) Yönetimi:** Giriş yapmış kullanıcıların forumda yeni başlık/gönderi açabilmesi, içeriklerini yayınlayabilmesi.
* **Gelişmiş Form Validasyonu:** `Flask-WTF` ve `WTForms` entegrasyonu sayesinde kullanıcı girdileri sunucu tarafında (backend) anlık olarak doğrulanır ve CSRF saldırılarına karşı korunur.
* **Dinamik Şablon Motoru:** `Jinja2` kullanılarak kullanıcı durumuna göre (giriş yapmış/yapmamış) dinamik olarak değişen esnek arayüz yapısı.

---

## 🛠️ Kullanılan Teknolojiler & Kütüphaneler

Projenin arkasında çalışan güçlü Python ekosistemi bileşenleri:

* **Framework:** [Flask](https://flask.palletsprojects.com/) (Python tabanlı mikro web framework)
* **ORM / Veritabanı:** `Flask-SQLAlchemy` (SQL veritabanı ilişkilerini kolayca yönetmek için)
* **Form Yönetimi:** `Flask-WTF` & `WTForms` (Güvenli ve validasyonlu form yapıları)
* **Güvenlik / Kriptografi:** `Werkzeug` (Şifre hashleme ve doğrulama mekanizmaları)
* **Template Engine:** `Jinja2` (HTML sayfalarını dinamik veriyle beslemek için)

---

## 📂 Klasör Yapısı

Proje, Flask'ın en temiz ve genişletilebilir pratiklerine uygun olarak modüler bir düzende kurgulanmıştır:

```text
├── forms.py         # Kayıt, giriş ve gönderi formlarının (WTForms) tanımları
├── models.py        # Veritabanı şemaları (User, Post modelleri ve ilişkileri)
├── static/          # CSS, JavaScript ve görseller gibi statik dosyalar
├── templates/       # Jinja2 tabanlı dinamik HTML şablonları (layout, login, register vb.)
└── app.py           # Uygulamanın ana giriş noktası, route tanımları ve config ayarları
