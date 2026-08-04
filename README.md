# JPEG-6502

Eksperymentalny prototyp kompresora i dekodera obrazu zorientowanego na MOS 6502, z własnym formatem archiwum J650 oraz szkicem dekodera w stylu MADS/6502.

## Co jest już gotowe

- format archiwum J650 z nagłówkiem i blokowym payloadem,
- kompresja oparta o prosty model bloków 8×8 i wybór współczynników po transformacie DCT,
- generator szkicu dekodera 6502 w formie pliku assembly,
- eksport podglądu `.xex` dla Atari 8-bit,
- eksport podglądu PNG z dekompresją i odwzorowaniem kolorów do stylu Atari,
- interfejs CLI do całego pipeline’u,
- obsługa trybów ANTIC D, E i F,
- pakiet Python z layoutem `src/` i entry pointem konsolowym `switch`.

## Ograniczenia projektu

- dekoder 6502 jest nadal szkicem prototypowym, a nie pełnoprawnym, zoptymalizowanym implementacją hardware’ową,
- obecny model kompresji jest stratny i oparty na zachowaniu wybranych współczynników w bloku 8×8,
- pamięć dekodera jest nadal ograniczona do prostego, eksperymentalnego modelu,
- w aktualnym szkicu dekodera brak jeszcze pełnego odwzorowania rekonstrukcji z bazowych bloków i pełnej arytmetyki Q8.8.

## Szybki start

### 1. Instalacja

Z repozytorium uruchom:

```bash
python -m pip install -e .
```

Dzięki temu projekt jest dostępny jako moduł Pythona oraz jako skrypt konsolowy `switch`.

### 2. Przez CLI

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

Alternatywnie po instalacji można użyć:

```bash
switch sample.bin \
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

Przykładowo:
- `--antic-mode E` oznacza 160×192 obrazu w 2 bpp / 4 kolory,
- `--palette` przyjmuje 4 wartości dla kolorów pikseli `0..3` (opcjonalnie można podać 5. wartość jako kolor tła),
- `--keep-coeffs` kontroluje poziom kompresji: niższa wartość = mniejszy plik, ale gorsza jakość,
- `--export-png` tworzy podgląd obrazu w formacie PNG,
- `--scale` zwiększa rozdzielczość PNG przez skalowanie najbliższego sąsiada.

### 3. Przez Python API

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

## Testy

```bash
python -m pytest -q
```

## Notatka o kolorach

W trybie ANTIC E (2 bpp / 4 kolory) `--palette` powinien zawierać 4 wartości odpowiadające kolorom dla wartości pikseli `0..3`. W trybie ANTIC F (1 bpp / 2 kolory) należy podać 2 wartości. Dodatkowa piąta wartość może być użyta jako kolor tła, jeśli taki jest wymagany przez konkretny workflow.
