# 3Gen Case Study

Bu proje **docker compose** ile ayağa kalkan basit bir case study'dir. İçinde **FastAPI**, **Celery**, **PostgreSQL** ve **Redis** bulunur. Amaç görsel işleme pipeline'ını uçtan uca göstermektir.

Kullanıcı bir proje oluşturur, frontend tarafında görsel üzerinde koordinatları ayarlar. Burada **fabric.js** kullanılır; yani canvas üzerinde sürükle-bırak, ölçekleme, önizleme gibi işlemler bu kütüphane üzerinden yapılır. Backend tarafında ise işin mutfak kısmını **Pillow** üstlenir. **Celery worker**, feed'den ürün görsellerini indirir, frame ile birleştirir, gerekirse köşeleri yuvarlar ve **output** klasörüne kaydeder.

---

## Teknolojiler

- **FastAPI** → API katmanı, proje ve kullanıcı işlemleri
- **Celery** → Arka plan görevleri (görsellerin işlenmesi)
- **PostgreSQL** → Veritabanı
- **Redis** → Celery broker/queue
- **Pillow** → Backend'de görselleri birleştirme ve işleme
- **fabric.js** → Frontend tarafında canvas üstünde görsel önizleme

Tüm servisler `docker compose` ile tek komutla çalışır. `.env` dosyası repoda olduğu için ayrıca ayar yapmaya gerek yoktur.

---

## Kurulum

Projeyi kendi makinenizde çalıştırmak için repoyu klonladıktan sonra sırasıyla build alıp servisleri ayağa kaldırmanız gerekir:

```bash
git clone https://github.com/FurkanGulenc/3gen-CaseStudy.git
cd 3gen-CaseStudy

docker compose build
docker compose up -d
```

### Notlar

- Docker'ın eski sürümlerinde `docker-compose` komutunu kullanmanız gerekebilir.
- Servislerin çalışması için şu portların boş olması gerekir:
  - **8080** → FastAPI
  - **5432** → PostgreSQL
  - **6380** → Redis

## Çalıştırma Sonrası

Komutlardan sonra bütün servisler ayağa kalkmış olacaktır:

- **FastAPI** → http://localhost:8080
- **PostgreSQL** → `localhost:5432`
- **Redis** → `localhost:6380`
- **Celery worker** → Arka planda çalışır

`.env` dosyası repoda hazır geldiği için ayrıca ayar yapmaya gerek yoktur.

## Process Sonuçlarını Kontrol Etme

Process işlemi tamamlandığında görseller container'ın içindeki `media/outputs/{projectID}` dizinine kaydedilir.

Kontrol etmek için:

```bash
docker exec -it fastapi_app bash
ls media/outputs/{projectID}
```

Çıkan dosyaları kendi makinenize kopyalamak için:

```bash
docker cp fastapi_app:/app/media/outputs/{projectID} .
```