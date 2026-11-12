# FlaskileForum — ctrl_shift_n

Flask ve MySQL ile yazdığım bir yazı paylaşım uygulaması. Kullanıcılar hesap açıp yazı ekleyebiliyor, kendi yazılarını düzenleyebiliyor ve diğer yazılara yorum bırakabiliyor.

Profil sayfalarında biyografi ve avatar var. Yönetici panelinden yazılar ve yorumlar kaldırılabiliyor.

## Kod düzeni

Uygulamanın route'ları, formları ve veritabanı sorguları `blog.py` içinde. Sayfalar `templates` klasöründeki Jinja şablonlarıyla hazırlanıyor. MySQL bağlantısı `flask_mysqldb`, parola işlemleri `passlib`, formlar ise WTForms ile yapılıyor.

## Çalıştırma

Bir Python sanal ortamında bağımlılıkları kur:

```sh
python -m pip install -r requirements.txt
```

MySQL bağlantısı için `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` ve `MYSQL_DB` ortam değişkenlerini tanımla. Veritabanında `users`, `articles` ve `comments` tablolarının da hazırlanmış olması gerekiyor; depoda bunları oluşturan bir SQL kurulum dosyası bulunmuyor.

Ardından uygulamayı başlat:

```sh
python blog.py
```

Varsayılan port `5000`; farklı bir port için `PORT` ortam değişkeni kullanılabiliyor.
