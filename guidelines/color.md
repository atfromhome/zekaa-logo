# Warna

| Nama | HEX | RGB | CMYK perkiraan | Peran |
|---|---|---|---|---|
| Arus | `#0B7A64` | 11 122 100 | 91 0 18 52 | Ubin dan mark. Teks putih di atasnya 5,3:1 |
| Arus terang | `#0E9D81` | 14 157 129 | 91 0 18 38 | Teks aksen dan UI di tema gelap, 4,6:1 di atas Arang. Tidak dipakai untuk logo |
| Arang | `#1C2624` | 28 38 36 | 26 0 5 85 | Kata Zekaa, teks, latar gelap. 15,5:1 di atas putih |

CMYK adalah konversi mentah dari warna layar, bukan profil cetak. Arus cukup jenuh sehingga tampak lebih kusam di cetak proses; cocokkan ke Pantone fisik sebelum produksi.

## Warna per latar

| Latar | Berkas | Ubin | Mark | Kata |
|---|---|---|---|---|
| Putih atau terang | tanpa akhiran | Arus | putih | Arang |
| Arang atau gelap | `-dark` | Arus | putih | putih |
| Arus | `-inverse` | putih | Arus | putih |
| Foto | tanpa akhiran atau `-dark` | Arus | putih | putih di bagian gelap, Arang di bagian terang. Taruh di bagian foto yang rata |
| Cetak satu tinta | `-black` atau `-white` | hitam atau putih, mark dilubangi | | sama dengan ubin |

- Ubin Arus tetap terbaca di atas Arang, jadi logo tidak memakai Arus terang.
- Satu warna per bagian, tanpa gradien.
- Mark lepas memakai Arus di latar terang, putih di latar gelap dan Arus, atau hitam untuk satu tinta.
