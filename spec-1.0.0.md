**AKTUALNY ETAP DO IMPLEMENTACJI: ROADMAPA v1.0.0 (AI Assisted Encoder)**

 Agent AI ma skoncentrować się WYŁĄCZNIE na implementacji
 funkcjonalności opisanych w etapie **v1.0.0**. Nie należy rozpoczynać
 prac nad wersją v2.0 ani v3.0, chyba że będą prowadzone jako osobne
 eksperymenty.

------------------------------------------------------------------------

# Cel

Istnieje działający kodek JPEG-6502 wykorzystujący:

-   bloki 8×8
-   DCT
-   kwantyzację
-   ZigZag
-   RLE
-   prosty dekoder 6502

Uczenie maszynowe ma działać wyłącznie po stronie kompresora.

Dekoder powinien pozostać możliwie prosty (docelowo \<2 KB kodu) i nie
wykonywać żadnych obliczeń AI.

------------------------------------------------------------------------

# ROADMAPA PROJEKTU

## v1.0 --- Bazowy kodek (zrealizowane)

Zakres:

-   DCT
-   kwantyzacja
-   ZigZag
-   RLE
-   format J650
-   dekoder 6502

Status: **Ukończone / stan bazowy.**

------------------------------------------------------------------------

## ⭐ v1.0.0 --- AI Assisted Encoder (IMPLEMENTOWAĆ TERAZ)

To jest jedyny etap, który agent ma obecnie implementować.

Cele:

-   inteligentny wybór współczynników DCT,
-   adaptacyjna kwantyzacja,
-   adaptacyjna liczba zachowywanych współczynników,
-   eksperymentalny zapis (indeks współczynnika + wartość),
-   porównanie z klasycznym ZigZag.

Najważniejsze wymagania:

-   zachować zgodność z obecnym dekoderem wszędzie, gdzie to możliwe,
-   każdą zmianę ocenić pod względem wpływu na złożoność dekodera,
-   preferować inteligentniejszy kompresor zamiast bardziej złożonego
    dekodera.

Wyniki każdego eksperymentu mają zawierać:

-   rozmiar pliku,
-   PSNR,
-   SSIM,
-   liczbę współczynników,
-   liczbę par RLE,
-   czas kompresji.

------------------------------------------------------------------------

## v2.0 --- Learned Dictionary Codec (NIE IMPLEMENTOWAĆ)

Przyszły etap badawczy.

Możliwe kierunki:

-   dictionary learning,
-   sparse coding,
-   learned basis functions,
-   PCA,
-   K-SVD.

Dekoder nadal powinien wykonywać jedynie dodawanie i odczyty z tablic.

Nie rozpoczynać implementacji na obecnym etapie.

------------------------------------------------------------------------

## v3.0 --- Native Atari Codec (NIE IMPLEMENTOWAĆ)

Dalekosiężny kierunek rozwoju.

Zakres:

-   odejście od klasycznego DCT,
-   kodek uczony wyłącznie na grafice Atari,
-   rekonstrukcja oparta na prymitywach i tablicach,
-   ekstremalnie prosty dekoder 6502.

Jest to wyłącznie wizja przyszłego rozwoju projektu.

------------------------------------------------------------------------

# Zadania etapu v1.0.0

## 1. Inteligentny wybór współczynników

Model AI analizuje 64 współczynniki DCT i wybiera te, które warto
zachować.

Optymalizować:

-   jakość,
-   liczbę współczynników,
-   skuteczność RLE,
-   końcowy rozmiar pliku.

## 2. Adaptacyjna kwantyzacja

Wytrenować jedną lub kilka tablic kwantyzacji zoptymalizowanych dla
grafiki Atari.

## 3. Adaptacyjna liczba współczynników

Model decyduje ile współczynników pozostawić (DC, 4, 8, 12 itd.).

## 4. Eksperymentalny format

Przetestować zapis:

(indeks współczynnika, wartość)

przy zachowaniu minimalnych zmian w dekoderze.

------------------------------------------------------------------------

# Architektura

``` text
jpeg6502/
    encoder.py
    decoder6502.asm
    train_ai.py
    ai_selector.py
    adaptive_quantization.py
    dataset.py
    export_model.py
    experiments/
```

------------------------------------------------------------------------

# Kryteria sukcesu

-   ≥10% mniejszy plik przy tej samej jakości,
-   lub wyższy PSNR/SSIM przy tym samym rozmiarze,
-   lub wyraźnie lepsza skuteczność RLE.

Priorytetem jest rozwój kompresora, nie dekodera.
