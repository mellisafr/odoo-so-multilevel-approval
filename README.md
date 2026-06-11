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

## Cara Install

### 1. Letakkan modul di addons path

Clone atau salin folder modul ke direktori `custom_modules` Anda:

```bash
cd /odoo17/custom_modules
git clone https://github.com/<user>/odoo17-sales-approval.git
```

**Penting:** rename folder hasil clone menjadi nama teknikal modul, yaitu
`sales_approval`. Nama folder harus sama persis dengan technical name modul agar
Odoo dapat mengenalinya.

```bash
mv odoo17-sales-approval sales_approval
```

Pastikan direktori tersebut terdaftar pada `addons_path` di file konfigurasi Odoo
(`odoo.conf`):

```ini
[options]
addons_path = /odoo17/addons,/odoo17/custom_modules
```

### 2. Restart Odoo dan aktifkan mode developer

```bash
./odoo-bin -c odoo.conf
```

Lalu masuk ke **Settings → Activate the developer mode**.

### 3. Update Apps List dan install

1. Buka menu **Apps**.
2. Klik **Update Apps List**.
3. Cari **Sales Approval**, lalu klik **Activate / Install**.

Alternatif lewat command line (langsung install/upgrade ke database tertentu):

```bash
# install pertama kali
./odoo-bin -c odoo.conf -d <nama_db> -i sales_approval --stop-after-init

# upgrade setelah ada perubahan kode
./odoo-bin -c odoo.conf -d <nama_db> -u sales_approval --stop-after-init
```

### 4. Konfigurasi pasca-install

1. **Set kategori gudang** — Inventory → Configuration → Warehouses, isi field
   **Approval Category** pada tiap gudang:
   - `Store` → Store (Ritel)
   - `Internal 3PL` / `Factory` → Internal / 3PL
2. **Set approver** — Settings → Users:
   - Internal/3PL: beri user group **Inventory / Administrator** (`stock.group_stock_manager`).
   - Store: centang group **SO Approver (Store)**.

## Dependensi

- `sale_management`
- `sale_stock`

## Lisensi

LGPL-3
