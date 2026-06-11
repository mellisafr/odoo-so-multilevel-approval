# Sales Approval (Odoo 17)

Modul custom Odoo 17 untuk **approval Sales Order berlapis** berdasarkan kategori gudang
(Store vs Internal/3PL), dengan pengecekan **attempt harian** dan **lampiran Berita Acara
kondisional** (file, foto, atau URL).

## Aturan Approval

| Gudang | Attempt | Approval | Berita Acara |
|--------|---------|----------|--------------|
| Store (Ritel) | SO ke-1 hari itu | Tidak | Tidak |
| Store (Ritel) | SO ke-2 dst (hari sama) | Ya (user tertentu) | Wajib |
| Internal / 3PL | Setiap submission | Ya (WH Manager, 1 layer) | Wajib |

## Cara Kerja

- Setiap `stock.warehouse` diberi field **Approval Category** (`store` / `internal_3pl`).
- `sale.order` menurunkan kategori tersebut lewat field related `so_approval_category`.
- Saat konfirmasi SO, modul menghitung jumlah attempt pada gudang & hari yang sama
  menggunakan `search_count` lalu menentukan apakah approval + Berita Acara diperlukan.
- Bila wajib, SO tidak langsung terkonfirmasi melainkan masuk status **Menunggu Approval**,
  dan lampiran Berita Acara divalidasi terlebih dahulu.

## Instalasi

1. Salin folder `sales_approval` ke direktori `custom_modules` (addons path).
2. Restart service Odoo, lalu **Update Apps List**.
3. Install modul **Sales Approval**.
4. Buka tiap gudang (Inventory → Configuration → Warehouses) dan set **Approval Category**:
   - `Store` → Store (Ritel)
   - `Internal 3PL` / `Factory` → Internal / 3PL

## Dependensi

- `sale_management`
- `sale_stock`

## Lisensi

LGPL-3
