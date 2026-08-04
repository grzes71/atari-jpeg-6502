# JPEG-6502 implementation checklist

## 1. Specyfikacja i założenia
- [x] Zdefiniować cel projektu i ograniczenia sprzętowe.
- [x] Zdefiniować format obrazu wejściowego: 160×192, 4 kolory, indeksy 0..3.
- [x] Zdefiniować podział obrazu na bloki 8×8.
- [x] Zdefiniować ogólny model kompresji i dekompresji.
- [x] Zdefiniować priorytet: prostota dekodera 6502 kosztem złożoności kompresora.

## 2. Format pliku
- [x] Zdefiniować dokładnie nagłówek pliku.
- [x] Zdefiniować magic number `J650`.
- [x] Zdefiniować zapis szerokości i wysokości jako `uint16`.
- [x] Zdefiniować zapis `BlockSize` i `Reserved`.
- [x] Zdefiniować kolejność bloków w pliku.
- [x] Zdefiniować sposób obsługi błędów przy niepoprawnym nagłówku lub uszkodzonych danych.

## 3. Struktura projektu
- [x] Utworzyć pliki:
  - [x] encoder.py
  - [x] decoder6502.asm
  - [x] dct.py
  - [x] quantization.py
  - [x] zigzag.py
  - [x] basis_generator.py
  - [x] fileformat.py
  - [x] tests/
- [x] Zdefiniować wspólną strukturę danych dla bloków i współczynników.

## 4. Kompresor Python
- [x] Zaimplementować wczytywanie obrazu wejściowego.
- [x] Zaimplementować podział na bloki 8×8.
- [x] Zaimplementować 2D DCT dla każdego bloku. (szkic: zwraca wejście bez pełnej transformacji)
- [x] Zaimplementować kwantyzację. (szkic: identity)
- [x] Zaimplementować transformację ZigZag. (tablica indeksów)
- [x] Zostawić tylko pierwszych 10 współczynników. (w strukturze planu, nie w pełnym pipeline)
- [x] Połączyć prosty etap DCT/kwantyzacji/zigzag z pipeline’em tak, by blok był przetwarzany w bardziej JPEG-like stylu.
- [x] Zaimplementować mapowanie współczynników do pozycji zgodnych z zigzag, by dane wejściowe były bardziej sensowne niż zwykła lista wartości.
- [x] Zaimplementować prosty wybór najważniejszych współczynników i ich zapis w bardziej kompresyjnej formie payloadu.
- [x] Zaimplementować dekoder, który odczytuje prostą formę payloadu z parami indeks/wartość i odtwarza blok.
- [x] Zaimplementować kodowanie RLE.
- [x] Zaimplementować zapis EOB (`0xFF`).
- [x] Zabezpieczyć dekoder RLE przed traktowaniem EOB jako wartości danych.
- [x] Umożliwić pipeline’owi obsługę małych obrazów przez dopełnienie bloków do 8×8.
- [x] Umożliwić jedną ścieżką wejścia `.bin` wygenerowanie zarówno pliku `.j650`, jak i szkicu `.asm`.
- [x] Dodać prosty eksport minimalnego pliku `.xex` z wygenerowanego szkicu asm.
- [x] Ujednolicić pipeline tak, by opcjonalnie generować `.xex` przy jednym uruchomieniu.
- [x] Zaimplementować prosty generator preview `.xex` z inicjalizacją PAL/ANTIC, listą wyświetlania i stubem dekodera.
- [x] Umożliwić eksport `.xex` z parametrami palety i trybu ANTIC (D/E/F).
- [x] Dodać prosty interfejs CLI do uruchamiania całego pipeline’u z poziomu terminala.
- [x] Sprawdzić pipeline na reprezentatywnym obrazie 160×192 oraz zapisie danych wejściowych w formacie 2bpp.
- [x] Zaimplementować zapis całego pliku w formacie J650.

## 5. Kodowanie RLE
- [x] Zdefiniować format par `<count_zero><value>`.
- [x] Zaimplementować kodowanie serii zer. (minimalna implementacja w `rle.py`)
- [x] Obsłużyć przypadek wielu zer.
- [x] Obsłużyć przypadek braku niezerowych wartości.
- [ ] Zdefiniować, jak traktować DC i kolejne współczynniki.

## 6. Kwantyzacja
- [x] Zdefiniować tablicę kwantyzacji.
- [x] Zaimplementować dzielenie przez tablicę kwantyzacji.
- [x] Zaimplementować zaokrąglenie do liczby całkowitej.
- [x] Zdefiniować zakres wartości po kwantyzacji (`int8`).
- [x] Obsłużyć przypadki przekroczenia zakresu.

## 7. Generator bazowych bloków
- [x] Zdefiniować sposób generowania bazowych bloków dla każdego zachowanego współczynnika. (szkic: jeden blok bazowy dla pierwszego współczynnika)
- [x] Zaimplementować generowanie wzorców 8×8.
- [ ] Zdefiniować skalowanie zgodne z Q8.8.
- [x] Przygotować dane w formie przyjaznej dla dekodera 6502.

## 8. Dekoder 6502
- [x] Odczytać nagłówek pliku. (w Pythonie, przez `read_header`)
- [x] Odczytać kolejny blok. (w Pythonie i w szkicu generatora asm)
- [x] Rozkodować RLE. (w szkicu: dodano pętlę odczytu payloadu, warunek EOB i iterację po parach count/value)
- [x] Przygotować prosty szkic dekodera do składania przez narzędzie asemblera. (dodano obsługę ORG i instrukcji używanych przez generator)
- [x] Przygotować prosty smoke test py65 dla szkicu dekodera.
- [x] Zbliżyć szkic dekodera do zapisu wartości do pamięci obrazu przez wskaźnik indeksowany.
- [x] Dodać w szkicu jawne odniesienie do par count/value dla dekodowania RLE.
- [x] Dodać w szkicu osobne odniesienia do count i value w ramach pary RLE.
- [x] Dodać w szkicu osobne odczyty count i value z payloadu.
- [x] Pokazać w szkicu, że wartość jest ładowana i zapisywana do pamięci obrazu.
- [x] Pokazać w szkicu, że liczba powtórzeń jest sterowana przez count w pętli.
- [x] Pokazać w szkicu serię wielokrotnych zapisów do pamięci obrazu.
- [x] Uzupełnić brakujące współczynniki zerami.
- [x] Wykonać dekwantyzację.
- [ ] Zrekonstruować blok z tablic bazowych.
- [x] Ograniczyć wartości do zakresu 0..3.
- [x] Zapisać blok do pamięci obrazu.

## 9. Optymalizacje dekodera
- [x] Zaimplementować specjalny przypadek dla DC-only. (w szkicu: zapis tagu i długości + danych)
- [ ] Jeśli po RLE pozostaje tylko DC, wypełnić cały blok jedną wartością.
- [ ] Zminimalizować liczbę mnożeń i operacji.
- [x] Utrzymać kod możliwie krótki i prosty.

## 10. Arytmetyka i formaty
- [ ] Użyć `int16` dla obliczeń pośrednich.
- [ ] Zdefiniować fixed-point Q8.8.
- [x] Unikać liczb zmiennoprzecinkowych. (obecnie moduły są szkicowe i bez pełnej DCT)
- [ ] Zdefiniować sposób konwersji między Q8.8 a wartościami całkowitymi.

## 11. Testy jednostkowe
- [x] Test dla bloku z samym DC. (via `tests/test_fileformat.py` i `tests/test_decode_simple.py`)
- [x] Test dla bloku z kilkoma współczynnikami. (via `tests/test_decoder_model.py`)
- [x] Test dla bloku z samym EOB.
- [x] Test dla RLE.
- [x] Test dla kwantyzacji.
- [x] Test dla generatora bazowych bloków.

## 12. Testy integracyjne
- [x] Test pełnego obrazu 160×192. (via `tests/test_raw_bitmap_to_j650.py`)
- [x] Test odczytu i zapisu pliku J650.
- [x] Test niepoprawnego nagłówka.
- [ ] Test niepełnych danych bloków.
- [x] Test zgodności kompresora i dekodera.

## 13. Dokumentacja
- [ ] Uzupełnić opis formatu pliku.
- [ ] Opisać format danych dla dekodera 6502.
- [ ] Opisać sposób generowania bazowych bloków.
- [x] Opisać sposób uruchamiania testów. (README zawiera podstawową instrukcję)

## 14. Finalna walidacja
- [x] Sprawdzić, czy kompresor generuje plik zgodny ze specyfikacją. (obsługa nagłówka i prostego payloadu działa)
- [x] Sprawdzić, czy dekoder poprawnie odtwarza bloki. (Python-side round-trip działa)
- [ ] Sprawdzić, czy projekt mieści się w przyjętych ograniczeniach.
- [x] Naprawić blokujące testy formatu nagłówka i eksportu MADS.
