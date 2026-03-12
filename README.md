# WebScraping — Texnomart.uz

Texnomart.uz saytidan mahsulotlarni avtomatik yig'ib `products.json` fayliga saqlovchi scraper. SOLID arxitekturasi asosida qurilgan.

## O'rnatish

```bash
pip install -r requirements.txt
cp .env.example .env
```

## Ishlatish

### 1. Bitta yoki bir nechta URL scraping

```bash
python -m app.main scrape --url https://texnomart.uz/product/detail/354961/
```

### 2. Texnomart kategoriya scraping

```bash
python -m app.main scrape-texnomart --catalog-url https://texnomart.uz/katalog/aksessuary-dlya-telefonov/ --max-products 30
```

### 3. To'liq do'kon scraping (barcha kategoriyalar, sahifalash)

```bash
python scrape_catalog.py
python scrape_catalog.py --max-pages 5 --delay 1.0
```

Yoki faqat ba'zi kategoriyalar:

```bash
python -m app.main scrape-texnomart-store \
  --category-url https://texnomart.uz/katalog/smartfony/ \
  --category-url https://texnomart.uz/katalog/noutbuki/ \
  --max-pages-per-category 5
```

### 4. Telefon mahsulotlarini qo'shish

```bash
python add_phone_products.py
```

### 5. Lokal HTML fayldan parse qilish (debug uchun)

```bash
python -m app.main parse-local-product --html-file app/product_page.html --source-url https://texnomart.uz/product/detail/354961/
```

Natija `products.json` faylida saqlanadi.

## Arxitektura

```
app/
├── domain/          # Entity va interfeylar
├── application/     # Use case-lar
├── infrastructure/  # HTTP, parser, JSON repository
└── core/            # Config va logging

scrape_catalog.py    # To'liq katalog scraper (Rich progress bar bilan)
add_phone_products.py # Telefon mahsulotlarini qo'shish skripti
products.json        # Natija fayl
```
