# Nocne piloty v2 — 3/4 października 2026

## Wynik pierwszego etapu — około 04:35

DSAC080 bez kary entropii zakończył 145 412 kroków i 33 853 aktualizacje,
z zerowym zaległym kredytem. W treningu 0/246 ukończeń, maksymalny postęp
62,9%. Ewaluacja końcowego checkpointu: 0/3 ukończeń, postęp 78,9%, 5,4%,
5,4%. Entropia zbliżyła się do celu, lecz konfiguracja nie zapewniła stabilnej
jazdy i **nie jest zakwalifikowana do pełnych treningów**. Szczegóły oraz
następny, nieuruchomiony pilot celu entropii 2,0 są w [READINESS.md](READINESS.md).
TQC wystartował o 04:10 Europe/Warsaw; kolejka dalej wykonuje pierwotne
pozostałe etapy. To wynik częściowy, nie końcowy raport całej kampanii.

## Aktualizacja po audycie DSAC — 4 października, około 02:00

Aktualny plan zastępuje kolejność opisaną niżej. Po zgodzie Jakuba zapisano
i zakończono kontrolny DSAC080 z karą entropii 0,5. Końcowy checkpoint ma
21 997 aktualizacji. Próba jest krótsza niż budżet 145 408 kroków; porównanie
treningu trzeba ograniczyć do wspólnego budżetu kroków, podając aktualizacje.

Audyt na checkpointcie 15 000 aktualizacji potwierdził poprawny kierunek
regulacji temperatury, uczenie prostego bandyty i brak blokowania gradientów
krytyka przez clipping w badanej próbce. Kara względem entropii wolno
aktualizowanego aktora znosiła około 80% projekcji surowego gradientu wartości.
To nie jest pomiar zmiany kroku optymalizatora Adam. Na dwóch osobnych kopiach
aktora, po 200 aktualizacjach przy zamrożonych Q i alpha, entropia wynosiła
4,126 z karą 0,5 oraz 2,798 bez kary. To diagnostyka jednej próbki replayu,
a nie wynik jazdy ani dowód przewagi algorytmu.

Dwa przejazdy deterministyczne końcowego kontrolnego checkpointu dały
0/2 ukończeń i około 0,5% postępu, bez błędów telemetryki lub kontrolera.
Kontrolny DSAC nie jest zakwalifikowany do pełnych treningów.

Nowa kolejność:

1. Ewaluacja kontrolnego DSAC080: 2 przejazdy (zakończona).
2. DSAC080 od zera, z `entropy_penalty_coefficient: 0.0`, następnie 3 przejazdy.
3. TQC, następnie 2 przejazdy.
4. PPO, następnie 2 przejazdy.
5. IQN, następnie 2 przejazdy.
6. QR, następnie 2 przejazdy.

Nowy DSAC zmienia tylko karę entropii, zachowując cel `0.8 * ln(78)`, seed 17,
model i budżet. Próba z celem 0,98 została odroczona. Konfiguracja przenośna:
`configs/diagnostic/discrete-sac-entropy080-beta000-s17.yaml`.
Ustawień pełnego DSAC nie zmieniono przed uzyskaniem wyników rzeczywistego pilota.

Aktualną kolejkę wskazuje `artifacts/tmrl-test-comparison/active-queue.json`
w głównym repozytorium Jakuba. Jest to `queue-overnight-dsac-ab-20261004`;
jej zewnętrzny `runner.py` i konfiguracje zachowują zamrożone źródła pakietów.
Każdy pilot ma limit 2 h 15 min. Runner rozpoczyna zapis najpóźniej o 13:50
Europe/Warsaw, pozostawiając do 10 minut na zamknięcie przed 14:00.
Nie rozpoczyna następnego kontrolera, dopóki poprzedni i jego potomkowie nie zakończą pracy.

Krótkie ewaluacje mają wyłączone progi wyniku. Komunikat „Benchmark passed”
oznacza tu poprawne wykonanie diagnostyki, nawet przy 0 ukończeń; nie kwalifikuje
algorytmu do pełnego treningu. Wynik oceniać z `evaluation.json`, postępu,
ukończeń, strat, entropii i błędów. Finalny protokół nadal wymaga 30 przejazdów
na każdy seed. Pełne treningi nie uruchomią się automatycznie.

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
