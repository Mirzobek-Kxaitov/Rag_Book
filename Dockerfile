# Python 3.10 asosidagi rasmiy image
FROM python:3.10-slim

# Ish katalogini o'rnatish
WORKDIR /app

# Tizim paketlarini yangilash va kerakli kutubxonalarni o'rnatish
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Requirements faylini nusxalash va o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini nusxalash
COPY . .

# .env faylini tekshirish (agar mavjud bo'lmasa, ogohlik berish)
RUN if [ ! -f .env ]; then \
    echo "WARNING: .env file not found. Make sure to provide environment variables."; \
    fi

# Static papkasini yaratish
RUN mkdir -p static

# Port ochish
EXPOSE 7860

# Gradio ilovasini ishga tushirish
CMD ["python", "gradio_file.py"]