# 🌋 Manado AI Language Analyzer V2.0

![Manado AI Hero](https://img.shields.io/badge/Status-Version%202.0%20Live-brightgreen?style=for-the-badge&logo=fastapi)
![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20GSAP%20%7C%20Tailwind-blue?style=for-the-badge)
![Compliance](https://img.shields.io/badge/Standard-BMM%202026-ff69b4?style=for-the-badge)

**Manado AI Analyzer** adalah platform analisis linguistik tercanggih untuk Bahasa Manado. Menggabungkan kekuatan **FastAPI** di backend dengan estetika modern **Next.js-style UI (GSAP + Tailwind)** untuk memberikan pengalaman analisis bahasa yang akurat, interaktif, dan premium.

---

## ✨ Fitur Unggulan

### 1. 🔍 Validasi SPOK (BMM 2026)
Sistem otomatis mengurai struktur kalimat berdasarkan standar tata bahasa Manado terbaru (**BMM 2026**). Mendeteksi Subjek, Predikat, Objek, dan Keterangan dengan presisi tinggi.

### 2. 🌐 Translasi Real-time
Terjemahan instan dari **Bahasa Manado ke Bahasa Indonesia**. Didukung oleh kamus lokal yang kaya (>700 kata) dan mendukung deteksi dialek khusus.

### 3. 🌳 Visual Parse Tree (Mermaid.js)
Transformasi kalimat mentah menjadi representasi visual pohon sintaksis (Syntactic Tree) yang elegan menggunakan **Mermaid.js**. Sangat membantu untuk studi Teori Bahasa dan Automata (TBO).

### 4. ✍️ Koreksi Typo "Did You Mean?"
Algoritma *Fuzzy Matching* yang cerdas untuk mendeteksi kesalahan ketik dan memberikan saran koreksi kata Manado yang paling mendekati secara real-time.

### 5. 🤖 Deteksi Tipe & Ragam
AI mengenali jenis kalimat (Deklaratif, Interogatif, Imperatif) serta ragam kalimat (Aktif/Pasif) berdasarkan marker linguistik dan prefix.

### 6. 📜 CFG Derivation Trace
Pelacakan langkah-demi-langkah proses pembentukan kalimat melalui aturan **Context-Free Grammar** (CFG) dari simbol ROOT hingga terminal.

---

## 🛠️ Stack Teknologi

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Frontend UI:** [Tailwind CSS](https://tailwindcss.com/) & [Vanilla JS](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- **Animations:** [GSAP](https://greensock.com/gsap/) (GreenSock Animation Platform)
- **Visuals:** [Mermaid.js](https://mermaid.js.org/) & [Particles.js](https://vincentgarreau.com/particles.js/)
- **Templates:** [Jinja2](https://jinja.palletsprojects.com/)

---

## 🚀 Cara Instalasi & Penggunaan

### Prasyarat
- Python 3.8+
- Git

### Langkah-langkah
1. **Clone Repository**
   ```bash
   git clone https://github.com/Joestar13/tbo_manado_ai.git
   cd manado-ai
   ```

2. **Setup Virtual Environment (Opsional)**
   ```bash
   python -m venv venv
   source venv/bin/scripts/activate  # Untuk Windows: venv\Scripts\activate
   ```

3. **Install Dependensi**
   ```bash
   pip install fastapi uvicorn jinja2
   ```

4. **Jalankan Aplikasi**
   ```bash
   uvicorn main:app --reload
   ```

5. **Akses di Browser**
   Buka `http://127.0.0.1:8000`

---

## 📂 Struktur Proyek

```text
├── main.py           # Entry point FastAPI & Routes
├── analyzer.py       # Core logic NLP & Grammar Engine
├── data.py           # Kamus & Data Vocabulary Manado
├── templates/        # Folder HTML (Jinja2)
│   ├── index.html    # Landing Page Premium
│   └── analyzer.html # Dashboard Analisis
└── README.md         # Dokumentasi Project
```

---

## 🎨 Design Philosophy
Aplikasi ini dirancang dengan estetika **Glassmorphism** dan **Vibrant Dark/Pink Mode** yang memberikan kesan futuristik. Setiap interaksi diperhalus dengan mikro-animasi GSAP untuk memberikan *user experience* kelas atas.

---

## 🤝 Kontribusi
Project ini dikembangkan untuk kebutuhan akademik dan pelestarian bahasa lokal. Jika Anda ingin berkontribusi dalam pengembangan kamus atau algoritma, silakan lakukan *Pull Request*.

**Made with ❤️ in Malang for Manado**
