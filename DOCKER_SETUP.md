## 1-Qadam: .env Faylini Tayyorlash

Loyiha ildiz katalogida `.env` fayl yarating va quyidagi ma'lumotlarni kiriting:

```bash
# .env fayl
PINECONE_API_KEY=sizning_pinecone_api_key
OPENAI_API_KEY=sizning_openai_api_key
PINECONE_ENVIRONMENT=us-east-1
```

**Eslatma**: `.env.example` faylidan nusxa olishingiz mumkin:

```bash
cp .env.example .env
```

Keyin `.env` faylini tahrirlang va o'z API kalitlaringizni kiriting.

## 2-Qadam: Docker Image Qurish
### Variant A: Docker Compose bilan (Tavsiya etiladi)

```bash
# Docker image qurish va konteynerlarni ishga tushirish
docker-compose up -d --build
```

## 3-Qadam: Ilovani Tekshirish

Ilova ishga tushgandan keyin, brauzeringizda quyidagi manzilni oching:

```
http://localhost:7860
```

## Docker Buyruqlari

### Konteynerlarni boshqarish

```bash
# Konteynerlarni to'xtatish
docker-compose down

# Konteynerlarni qayta ishga tushirish
docker-compose restart

# Konteyner loglarini ko'rish
docker-compose logs -f

# Faqat ilovaning logini ko'rish
docker-compose logs -f gradio-app

# Ishlab turgan konteynerlarni ko'rish
docker ps

# Konteynerni to'xtatish
docker stop beruniy-ai-app

# Konteynerni o'chirish
docker rm beruniy-ai-app
```