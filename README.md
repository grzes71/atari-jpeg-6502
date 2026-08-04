# JPEG-6502

Eksperymentalny prototyp kompresora i dekodera obrazu zorientowanego na MOS 6502, z własnym formatem archiwum J650 oraz szkicem dekodera w stylu MADS/6502.

## Co jest już gotowe

- format archiwum J650 z nagłówkiem i blokowym payloadem,
- kompresja oparta o DCT, kwantyzację, ZigZag i RLE na blokach 8×8,
- **v1.0.0 — AI-Assisted Encoder**: heurystyczny selektor współczynników (zigzag / magnitude / hybrid), adaptacyjna liczba zachowywanych współczynników, trzy tablice kwantyzacji zoptymalizowane dla grafiki Atari (aggressive / balanced / fine), eksperymentalny format zapisu (indeks, wartość),
- generator szkicu dekodera 6502 w formie pliku assembly,
- eksport podglądu `.xex` dla Atari 8-bit,
- eksport podglądu PNG z dekompresją i odwzorowaniem kolorów do stylu Atari,
- metryki jakości PSNR i SSIM,
- harness eksperymentów porównujący strategie kompresji,
- interfejs CLI do całego pipeline’u,
- obsługa trybów ANTIC D, E i F,
- pakiet Python z layoutem `src/` i entry pointem konsolowym `switch`.

## Ograniczenia projektu

- dekoder 6502 jest nadal szkicem prototypowym, a nie pełnoprawnym, zoptymalizowanym implementacją hardware’ową,
- obecny model kompresji jest stratny i oparty na zachowaniu wybranych współczynników w bloku 8×8,
- pamięć dekodera jest nadal ograniczona do prostego, eksperymentalnego modelu.

## Szybki start

### 1. Instalacja

Z repozytorium uruchom:

```bash
python -m pip install -e .
```

Dzięki temu projekt jest dostępny jako moduł Pythona oraz jako skrypt konsolowy `switch`.

### 2. Przez CLI — pipeline klasyczny

```bash
python -m switch sample.bin \
  --width 160 \
  --height 192 \
  --output-bin output.j650 \
  --output-asm decoder.asm \
  --output-xex preview.xex \
  --export-png preview.png \
  --antic-mode E \
  --palette 0x00,0x02,0x08,0x0E \
  --keep-coeffs 10 \
  --scale 2
```

### 3. Przez CLI — AI-Assisted Encoder (v1.0.0)

```bash
# Tryb pixel (domyślny, zgodny z dekoderem 6502)
python -m switch sample.bin \
  --width 160 \
  --height 192 \
  --ai \
  --strategy hybrid \
  --quant-table balanced \
  --mode pixel \
  --output-bin output_ai.j650 \
  --output-asm decoder.asm

# Tryb coefficients (współczynniki DCT, tylko dekoder Python)
python -m switch sample.bin \
  --width 160 \
  --height 192 \
  --ai \
  --mode coefficients \
  --strategy zigzag \
  --keep-coeffs 8
```

Dostępne strategie (`--strategy`):
- `zigzag` — klasyczny porządek ZigZag,
- `magnitude` — współczynniki o największej amplitudzie,
- `hybrid` — adaptacyjna liczba współczynników z wagami pozycyjnymi.

Dostępne tablice kwantyzacji (`--quant-table`):
- `aggressive` — agresywna, najwyższa kompresja,
- `balanced` (domyślna) — zbalansowana,
- `fine` — wyższa jakość,
- `lossless` — brak kwantyzacji (identity), maksymalna jakość.

Tryb wyjścia (`--mode`):
- `pixel` (domyślny) — rekonstruuje piksele z wybranych współczynników DCT i zapisuje w formacie packed 16-bajtowym, w pełni zgodnym z dekoderem 6502,
- `coefficients` — zapisuje rzadkie współczynniki DCT jako pary (indeks, wartość); wymaga dekodera z obsługą dekwantyzacji i IDCT.

Przykładowo:
- `--antic-mode E` oznacza 160×192 obrazu w 2 bpp / 4 kolory,
- `--palette` przyjmuje 4 wartości dla kolorów pikseli `0..3` (opcjonalnie można podać 5. wartość jako kolor tła),
- `--keep-coeffs` kontroluje poziom kompresji: niższa wartość = mniejszy plik, ale gorsza jakość,
- `--export-png` tworzy podgląd obrazu w formacie PNG,
- `--scale` zwiększa rozdzielczość PNG przez skalowanie najbliższego sąsiada.

### 4. Przez Python API — pipeline klasyczny

```python
from pipeline import run_full_pipeline

run_full_pipeline(
    input_path="sample.bin",
    width=160,
    height=192,
    output_bin="output.j650",
    output_asm="decoder.asm",
    output_xex="preview.xex",
    antic_mode="E",
    palette=(0x00, 0x02, 0x08, 0x0E),
    keep_coeffs=10,
    export_png="preview.png",
    scale=2,
)
```

### 5. Przez Python API — AI-Assisted Encoder

```python
from pipeline import run_ai_pipeline, run_experiment
from ai_selector import SelectionConfig

# Pełny pipeline AI
run_ai_pipeline(
    input_path="sample.bin",
    width=160,
    height=192,
    output_bin="output_ai.j650",
    strategy="hybrid",
    quant_table="balanced",
    selector_config=SelectionConfig(min_keep=4, max_keep=64),
)

# Pojedynczy eksperyment z metrykami
result = run_experiment(
    "sample.bin",
    width=160,
    height=192,
    keep_coeffs=8,
    strategy="zigzag",
    quant_table="balanced",
)
print(result["psnr"], result["ssim"], result["file_size_bytes"])
```

## Wygenerowane pliki

Pipeline może wygenerować:

- `output.j650` – archiwum z danymi obrazu i nagłówkiem formatu J650,
- `decoder.asm` – szkic dekodera w stylu MADS/6502,
- `preview.xex` – prosty plik preview dla Atari 8-bit,
- `preview.png` – podgląd obrazu po dekompresji i odwzorowaniu kolorów.

## Kompresja i jakość

Obecna implementacja jest stratna. W każdym 8×8 bloku zachowuje się tylko wybrane współczynniki po transformacie, więc im mniej współczynników zostanie zachowanych, tym większa kompresja i większa utrata jakości.

Dopuszczalny zakres `--keep-coeffs` to `1..64`:
- `1` – wysoka kompresja, wyraźnie niższa jakość,
- `10` – domyślny balans między jakością a rozmiarem,
- `64` – praktycznie brak redukcji współczynników, najwyższa jakość, największy rozmiar pliku.

W praktyce wartości z zakresu `3..20` dają najbardziej sensowne przejścia między jakością a kompresją.

## Eksperymenty

Porównanie wszystkich strategii i tablic kwantyzacji w trybie pixel (6502-compatible):

```bash
python -m experiments.runner samples/witcher3.bin --width 160 --height 192 --output-json results.json
```

Przykładowe wyniki (witcher3.bin, 160×192, ANTIC E, tryb pixel):

```
Label                    PSNR     SSIM  Size(B)  Time(s)
-----------------------------------------------------------------
zigzag-k1               11.83   0.4412     1682    1.446
zigzag-k2               12.31   0.4873     4026    1.484
zigzag-k4               13.06   0.5346     4697    1.463
zigzag-k8               14.25   0.5892     5707    1.485
zigzag-k16              15.49   0.6408     5860    1.528
zigzag-k64                 inf   1.000     5841    1.510
```

Wynikiem jest tabela z PSNR, SSIM, rozmiarem pliku i czasem kompresji.

## Testy

```bash
python -m pytest -q
```

## Notatka o kolorach

W trybie ANTIC E (2 bpp / 4 kolory) `--palette` powinien zawierać 4 wartości odpowiadające kolorom dla wartości pikseli `0..3`. W trybie ANTIC F (1 bpp / 2 kolory) należy podać 2 wartości. Dodatkowa piąta wartość może być użyta jako kolor tła, jeśli taki jest wymagany przez konkretny workflow.
