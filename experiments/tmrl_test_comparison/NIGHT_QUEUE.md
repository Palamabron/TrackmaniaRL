# Nocne piloty v2 — 3/4 października 2026

## Zakres i podział

Jakub: IQN + QR. Borys: discrete SAC. Kamil: TQC. Kuba P.: PPO.
Pełne próby nadal wymagają oceny pilotów; kolejka nie uruchamia ich automatycznie.

Wersja v2 wprowadza na branch eksperymentów potrzebne części PR #52:
pomiar i korekcję skrętu, poprawkę skali prędkości i ograniczania postępu,
oraz głowy wartości w float32. Import ghostów nie jest częścią tej kampanii.
PR nie został scalony do main.

## Poprawki przed kolejką

- Zmierzono sterowanie na komputerze Jakuba i sprawdzono korekcję w grze.
  Wszystkie 13 poziomów jest rozróżnialnych; po korekcji maksymalny błąd
  to 0,00394 na skali [-1, 1]. Każdy komputer wymaga własnego pomiaru.
- Wszystkie konfiguracje włączają strict_update_budget. Kredyt aktualizacji
  nie jest ucinany ani przy dopływie danych, ani przy wznowieniu checkpointu.
  Po przekroczeniu progu 512 aktor czeka między epizodami i zwalnia sterowanie.
  Bieżący epizod może przekroczyć ten próg; to celowe, aby nie przerywać jazdy.
- Learner używa 2 wątków CPU. Krótki pomiar na tym komputerze dla discrete SAC,
  batch 256, wykazał około 5,00 aktualizacji/s przy 2 wątkach, 4,51 przy 4
  i 4,22 przy 24. To pomiar syntetyczny; logi jazdy są ostatecznym sprawdzeniem.
- Discrete SAC loguje teraz rzeczywistą średnią entropię polityki.
- PPO respektuje STOP po ukończeniu rolloutu i aktualizacji, zapisując checkpoint.
  Opóźnienie zatrzymania może wynieść około 2 minuty plus czas uczenia.
- PPO kończy ostatni epizod rolloutu jako truncation z bootstrapowaniem,
  zwalnia sterowanie na czas aktualizacji i rozpoczyna nowy epizod.
  Eliminuje to przejście oparte na starej obserwacji po przerwie w uczeniu.
  Jest to jawna różnica protokołu PPO: segment ma 2048 kroków (około 102,4 s).
- Wszystkie piloty mają budżet 145 408 kroków. Krótszy historyczny pilot IQN
  nie jest częścią porównania v2. Pilota ogranicza dodatkowo czas ścienny.

## Kolejność

1. discrete SAC, target_entropy = 0,8 * ln(78)
2. TQC
3. PPO
4. IQN
5. QR
6. discrete SAC, target_entropy = 0,98 * ln(78), próba kontrolna

Każda próba ma limit 2 h 15 min od uruchomienia procesu, potem żądanie zapisu
i maksymalnie 10 minut na bezpieczne zamknięcie. Ukończenie budżetu kroków
może zakończyć ją wcześniej. Około 13,5 h na całą kolejkę, do 14,5 h z narzutem
zatrzymywania. Treningi są od zera, seed 17, bez demonstracji i filtra referencyjnego.
Nie nazywać próby zatrzymanej limitem czasu ukończonym budżetem kroków.

Krótki test w grze przed kolejką: discrete SAC zebrał 288 kroków i wykonał
dokładnie 40 należnych aktualizacji po warmup 128 (UTD 0,25); PPO zebrał
2048 kroków i wykonał jedną aktualizację rolloutu. Oba zapisały checkpoint
i zsynchronizowały W&B. To test poprawności uruchomienia, nie jakości jazdy.

## Obsługa

Runner: `python -m experiments.tmrl_test_comparison.run_overnight KATALOG --key-source-root REPO_Z_ENV`.
Katalog zawiera schedule.json: listę obiektów name, config (pełna ścieżka),
run_id. Każdy YAML zachowuje metadane i własny identyfikator próby.
Runner wymaga klucza W&B, wymusza tryb online i domyślnie używa zespołu
dsc-pjatk-warsaw. Klucz jest ładowany do środowiska procesu, nigdy do konfiguracji.
Instalacja narzędzi: `uv sync --group dev`.

Plik STOP w katalogu kolejki zatrzymuje aktualny trening i następne etapy.
Runner zapisuje status.json, history.jsonl i osobne logi.
Nie ponawia automatycznie zakończonych lub błędnych prób. Błąd procesu albo
pozostawione procesy potomne zatrzymują kolejkę; najpierw ustalić przyczynę.
Przy przekroczeniu czasu zamykania nie uruchamia kolejnego kontrolera.

Kod i konfiguracje działającej próby są zamrożone. Nie modyfikować źródeł
w jej checkoutcie; przed poprawką zatrzymać i zapisać stan. Nie obchodzić
fingerprintu ani przenosić checkpointu do zmienionej konfiguracji.

## Decyzja przed pełnymi treningami

Sprawdzić checkpoint, W&B, skończone straty, postęp, entropię/alpha,
liczbę rzeczywistych aktualizacji, kredyt, odstępy decyzji i błędy telemetryki.
Po warmup expected_updates = floor((transitions - warmup) * UTD);
podczas pracy różnica może pozostawać w update_credit, ale nie może znikać.
Po zatrzymaniu limitem czasu zapisać zaległy kredyt; nie udawać, że został wykonany.

Wybór entropii discrete SAC oprzeć na dwóch próbach v2 oraz osobnej ewaluacji
bez eksploracji, a nie tylko najlepszym epizodzie treningowym. Porównywać przy
wspólnym budżecie kroków i raportować aktualizacje oraz czas. Konfiguracje pełne
discrete SAC zachowują dotychczasowy cel do rozstrzygnięcia tej próby.
TQC i PPO dopuścić po własnych pilotach. Na końcu zapisać wybrany wspólny commit,
konfiguracje trzech seedów, ustawienia hostów i raport z ograniczeniami.

Po pilotach wykonać krótką ewaluację kontrolną końcowych checkpointów,
jeśli pozwala pozostały czas. Ostateczne wyniki pełnych prób: 30 przejazdów
na seed, najlepiej na jednym komputerze. Nie ogłaszać przewagi algorytmu
na podstawie jednego seeda ani porównania dyskretnych i ciągłych akcji łącznie.
