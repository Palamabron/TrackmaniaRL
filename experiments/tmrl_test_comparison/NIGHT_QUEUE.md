# Nocne piloty v2 — 3/4 października 2026

## Powtarzalność IQN — 5 października, 08:11 Europe/Warsaw

Ocena zachowanego starego cp33854, na zamrożonym runtime d0dfe645, ukończona:
**29/30 met**, średnia ukończonych **49,452 s**, mediana **49,400 s**,
najlepsza **48,370 s**. Wszystkie 30 prób mają ważny timing:
29 587/29 587 pomiarów, max/p99 **50 ms**, brak błędów telemetrii/kontrolera.
Pominięte ramki **15 564**, maksimum 5. Wynik wspiera powtarzalność tej polityki
na seed17; nie dowodzi powtarzalności uczenia na trzech seedach ani celu 37 s.
Nie zmieniamy IQN arbitralnie po dawnym wyniku 1/2: baseline pozostaje.
Pełne nowe starty nadal wymagają wspólnego nowego commita, kalibracji lokalnej,
smoke i 30 końcowych prób dla każdego z seedów 17/29/43.
Dowód: `tmrl-overnight-diag-iqn-s17-benchmark-20261005T054442205511/evaluation.json`;
SHA checkpointu `ad4fabf38558c893ed54546143a47418eb3bc589925d828a95968f5a932d4f95`.
Istniejący runner rozpoczął TQC 08:10:48 Warsaw; SAC i QR pozostają w kolejce.
Kampania nadal trwa, SAVE 10:24 / HARD 10:34 bez zmian.

## Decyzja PPO — 5 października, 07:55 Europe/Warsaw

Porównanie obu wariantów zakończone na wspólnym cp70: **143 360 uczonych kroków /
70 aktualizacji**, pełne prefixy diagnostyczne, skończone checkpointy,
zgodność fingerprint i SHA potwierdzona. Pełnych miesięcznych treningów nie wykonano.

| Współczynnik entropii | Mety | Mediana ukończonych | Średnia ukończonych | Max/p99 kroku | Pominięte ramki |
| --- | --- | --- | --- | --- | --- |
| 0,01 baseline | 8/10 | 56,445 s | 56,585 s | 50/50 ms | 18 648 (max 6) |
| 0 | 7/10 | 57,880 s | 57,673 s | 50/50 ms | 18 173 (max 6) |

Wszystkie 20 prób mają ważny timing i brak błędów kontrolera/telemetrii.
Wariant 0 nie osiągnął minimum 8/10 met, miał niższy odsetek met oraz medianę
około 2,54% wolniejszą, zamiast wymaganych przynajmniej 5% poprawy.
**Zachowujemy baseline 0,01 w generatorze i pełnych konfiguracjach 17/29/43.**
Nie jest to dowód globalnej optymalności ani ukończenie końcowych 30 prób na seed.
Skoki race-clock treningu ponad 100 ms nadal stanowią ograniczenie lokalne.
Dowód decyzji: `queue-overnight-tuning-20261005/ppo-comparison-decision.json`.
Ocena wariantu 0: `tmrl-overnight-diag-ppo-entropy0-s17-benchmark-20261005T053439289662/evaluation.json`,
SHA cp70 `1646e5648265e9b5af3503c40feb4f9b0eb6ea256d2efaf30c05b5d244c29b83`.
Kampania trwa: istniejący runner rozpoczął 30 prób IQN 07:44:38 Warsaw.
SAVE 10:24 / HARD 10:34 bez zmian; pełny DSAC nadal zablokowany.

## PPO baseline — 5 października, 05:25 Europe/Warsaw

Świeży PPO entropy coefficient 0,01 zakończył krótki prefix diagnostyczny.
Do porównania wybrano potwierdzony, skończony cp70: **143 360 uczonych kroków,
70 aktualizacji**, processed_transitions=transitions; prefix_complete=true,
full_training_complete=false, wspólny harmonogram LR 2 048 000.
SHA256: `250767107f53a5917d9cc54fb8426539c8d234fd83a8dd01d09faf9bc8660bbb`.
Dziesięć prób greedy: **8/10 met**, średnia ukończonych 56,585 s,
mediana **56,445 s**, najlepsza 55,520 s. Dwie porażki przy około 81,20% postępu.
Wszystkie próby mają ważny timing; 11 068/11 068 pomiarów, max/p99 **50 ms**,
brak błędów kontrolera i telemetrii. Pominięte ramki: **18 648**, maksimum 6.
W treningu występowały skoki race-clock powyżej 100 ms (maksimum 530 ms);
poprawna ocena nie usuwa tego ograniczenia lokalnego treningu.
To wynik jednego seeda i 10 prób diagnostycznych, nie końcowe 30 prób na seed
ani dowód globalnej optymalności. Baseline 0,01 pozostaje ustawieniem domyślnym;
wybór 0 wymaga pełnego porównania zgodnego z ustalonym wcześniej protokołem.
Wariant entropy0 już działa od 05:21:32 Warsaw, W&B `yei92q7a`;
baseline `hymfpseo` potwierdzony finished. Kampania nadal trwa.
Dowody: `queue-overnight-tuning-20261005/ppo-baseline-completion.json` i
`tmrl-overnight-diag-ppo-baseline-s17-benchmark-20261005T031138975953/evaluation.json`.
SAVE 10:24 / HARD 10:34 pozostają nadrzędne; pełnych treningów nie uruchomiono.

## Wynik DSAC — 5 października, 03:10 Europe/Warsaw

Pilot celu entropii 2,0 / beta 0 zakończył **145 487 kroków / 33 871 aktualizacji**.
Końcowy cp33871 ma skończone tensory, zgodny fingerprint i rozliczony kredyt
**0,75** (`earned = accounted = 33 871,75`). Ocena zakończona: **0/10 met**,
postęp 4,24–5,17%, średnio 4,42%. Wszystkie pomiary czasu ważne, max/p99 50 ms,
brak błędów telemetrii/kontrolera; 651 pominiętych ramek, maksimum 5.
Warunek minimum 8/10 met NIE został spełniony: **pełny DSAC nadal zablokowany**,
hipoteza diagnostyczna nie zostaje promowana do konfiguracji seedów 17/29/43.
Poprawny zapis i sprawny pomiar nie oznaczają skutecznej polityki greedy.
Dowody: `queue-overnight-tuning-20261005/dsac-completion.json` oraz
`tmrl-overnight-diag-dsac-e200-b0-s17-benchmark-20261005T005546181914/evaluation.json`
w `artifacts/tmrl-test-comparison`. W&B trening `2fslk8zh`, ocena `vepn4pyj`.

To wynik częściowy kampanii. Świeży PPO baseline ruszył 02:58:36 Warsaw;
pozostałe etapy prowadzi istniejący runner. Nagroda i zamrożone runtime bez zmian.
Termin zapisu 10:24, twardy koniec 10:34 pozostają nadrzędne.


## Aktualna noc 4/5 października — jawne wznowienie

Nowy wskaźnik `active-queue.json`: `queue-overnight-tuning-20261005`.
Runner 37100, launcher 37184, start 00:50:18 Warsaw; zapis 10:24,
twardy koniec 10:34 5 października, 10 godzin od początku pracy o 00:34,
łącznie z przygotowaniem. `effective-deadline.json` i watchdog skracają
wewnętrzny limit runnera; nie prowadzą drugiego kontrolera.
DSAC resume → 10 ocen → PPO baseline prefix → 10 ocen → PPO entropy0 prefix
→ 10 ocen → po 30 ocen IQN/TQC/SAC/QR w pozostałym czasie. Dokładne warunki,
ograniczenia i zamrożone runtime opisuje [TUNING.md](TUNING.md).
Monitor co 5 minut, cisza przy zdrowym niezmienionym stanie. STOP zawsze
zatrzymuje; po wyniku całej kampanii lub terminie raport i PAUSED monitora.
Nie uruchamiać starego runnera, drugiego kontrolera ani pełnych eksperymentów.

## Historia: kolejka z 4 października 17:28, zatrzymana na polecenie użytkownika

Kod zespołu opublikowany na obu branchach: **8f440075**. Nowy pilot korzysta
z osobnego, czystego i zamrożonego `tmrl-tuning-runtime` na tym commicie.
Stare IQN/PPO będą oceniane na zachowanym `tmrl-algorithm-runs` (`d0dfe645`,
źródła Python `378f9c6a`), bez przenoszenia checkpointów między wersjami.

Kolejka `queue-tuning-20261004` wystartowała **17:27:56 Europe/Warsaw**.
Termin zapisu **20:17:56**, twardy koniec **20:27:56**. To zatwierdzone nowe
3 godziny łącznie, nie przedłużanie poprzedniej kampanii. Wskaźnik
`artifacts/tmrl-test-comparison/active-queue.json` wskazuje tę kolejkę.
DSAC `tmrl-tuning-dsac-entropy200-beta000-s17` działa, W&B
[o3aknhmz](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/o3aknhmz)
potwierdzony online/running. O 17:30 zapisano 1943 kroki w fazie warmup,
ważny timing ostatniego epizodu (p99 50 ms, max 60 ms), brak błędu telemetrii.
To kontrola uruchomienia, nie wynik uczenia ani kwalifikacja DSAC.

Następnie planowane są 10 ocen DSAC, 10 IQN i 5 PPO w pozostałym czasie.
Warunki promocji DSAC oraz sprawdzone ustawienia opisuje [TUNING.md](TUNING.md).
Monitor działa co 5 minut i ma zakończyć pracę po raporcie tej kampanii.
Pełnych treningów nie uruchomiono. Końcowy dobór DSAC pozostaje otwarty do
wyniku jazdy; jego pełne uruchomienia są nadal zablokowane.


## Nowe przygotowanie i testy — 2026-10-04 po 17:00

Po zakończeniu poprzedniej kampanii użytkownik zatwierdził naprawy oraz
**do 3 godzin łącznie nowych testów w grze**. Aktualne decyzje o parametrach,
kolejność prób, poprawki PPO i warunki wyboru DSAC opisuje [TUNING.md](TUNING.md).
Pełne treningi pozostają ręczne; DSAC nadal jest zablokowany do wyniku nowego
pilota. Stare checkpointy zachowują swój zamrożony runtime. Poniższy raport
15:41 i starsze sekcje dokumentują zakończoną poprzednią kampanię, nie nową kolejkę.

## Końcowy stan — 2026-10-04, 15:41 Europe/Warsaw

Kampania zakończona przed terminem 16:15. Autorytatywna kolejka
`queue-status-recovery-20261004` ma `queue_completed`, zakończenie
13:41:03 UTC. SAC trening zakończył 15:39:08: 145 416 kroków, 33 854
aktualizacje, kredyt 0,0, checkpoint finite, 83/198 met i ostatnie 20/20.
Ewaluacja 2/2: 43,78 i 44,75 s, średnia 44,265 s; ważne odstępy max/p99
50 ms, brak błędów, pominięte ramki 94/97 (max 3/1). W&B oba `finished`.
Dowód: `queue-status-recovery-20261004/sac-result.json`.

Nie pozostały żadne etapy. Nie uruchamiać ponownie starych runnerów,
supervisora SAC ani ukończonych pilotów. Wszystkie logi i checkpointy
zachowane; nie usuwano STOP. Brak nowej kolejki po terminie. Pełnych
treningów nie uruchomiono — są wyłącznie ręczne, po warunkach z
[HANDOFF.md](HANDOFF.md) i [READINESS.md](READINESS.md). DSAC nadal zablokowany.

Po zamknięciu wszystkich procesów sterujących grą przetestowano bezpośredni
reset nowego kodu, bez preflightu launchera i bez learnera: zgodny UID,
sukces po 12,922 s, race_time 10 ms, telemetria OK, klient i kontroler
zamknięte. `source-live-reset.json` zachowuje dowód. To lokalny test resetu;
smoke jazdy, kalibracja i timing każdego komputera nadal wymagane.

Monitor zostaje wyłączony po publikacji raportu końcowego. Źródła pilotów
pozostają na `378f9c6a` w zamrożonym checkoutcie; publikacja końcowa pochodzi
wyłącznie z nowego checkoutu zespołu. Poniższe sekcje są historią kampanii,
nie poleceniem dalszego uruchamiania.

## Historia kolejki

## Przejście do SAC — około 13:30

QR ukończył 145 425 kroków i 33 856 aktualizacji, kredyt 0,25. W treningu
53/174 met, ostatnie 19/20; końcowa ewaluacja 2/2: 57,07 s i 56,81 s.
Checkpoint oraz W&B sprawdzone. Continuous SAC ruszył 13:30:47,
`tmrl-test-v2-sac-s17`, W&B `dx93ox8g`. Pozostał wyłącznie SAC i jego eval;
runner tej samej `queue-status-recovery-20261004` dalej działa. Nie powtarzać
ukończonych etapów, nie uruchamiać starego supervisora. Granice 16:05/16:15
bez zmian; częściowy wynik QR nie wyłącza monitora całej kampanii.

## Aktualny plan — około 11:25

Po awarii atomowego zapisu statusu Windows stara kolejka nie uruchomiła
następnego etapu. IQN dokończył trening i zapis: 145 418 kroków, 33 854
aktualizacje, kredyt 0,5. Nie powtarzamy go ani DSAC/TQC/PPO. Dowody awarii
zachowano; nowa jawna kolejka `queue-status-recovery-20261004`, wskazywana
przez `active-queue.json`, zastępuje stary runner oraz supervisor SAC.
Pozostałe etapy: ewaluacja IQN (już 1/2 met, 49,90 s / 81,27%), QR, eval QR,
continuous SAC, eval SAC. QR ruszył 11:20, W&B `3gboyqdh` online.
Runner ma ponawianie zapisu przy blokadzie pliku oraz zapis i zatrzymanie
procesu dziecka przy awarii; cztery testy przeszły, w tym rzeczywista blokada
pliku w Windows. STOP w aktualnej lub poprzednich dwóch kolejkach blokuje
start; nie uruchamia się drugi kontroler. Źródła runtime pozostają zamrożone.
Każdy trening ma 145 408 kroków / 2 h 15 min, granica zapisu **16:05**,
koniec **16:15 Europe/Warsaw**. Starsze plany poniżej są historyczne.
Wyniki i ograniczenia: [READINESS.md](READINESS.md). Kampania nadal trwa.

## Rozszerzenie — około 09:20

Użytkownik dodał continuous SAC i zatwierdził termin 16:15 zamiast 14:00.
Po IQN i QR ruszy nowa kolejka SAC (145 408 kroków / 2 h 15 min + 2 eval).
Supervisor `queue-continuous-sac-20261004/after_queue.py` czeka na ukończenie
bieżącej kolejki i brak procesów sterujących grą; STOP lub awaria blokuje start.
Wskaźnik pending: `PENDING-SAC.json`, po starcie zmieni się `active-queue.json`.
Nowa granica zapisu 16:05. Stary runner IQN/QR zachowuje granicę 13:50;
eventualny krótszy QR wymaga jawnej kontynuacji, jeśli pozostaje czas.
SAC przeszedł schema/CPU update/checkpoint round-trip, model i nagroda jak TQC.
PPO ukończony: 2/2 eval, 58,27 s i 59,13 s. Wyniki, audyt i ograniczenia
opisano w [ALGORITHM_AUDIT.md](ALGORITHM_AUDIT.md).
To nadal kampania pilotów, pełne treningi nie startują automatycznie.

## Aktualizacja — około 06:45

TQC zakończył pełny pilot: 145 433 kroki, 33 858 aktualizacji, kredyt 0,25,
71/181 ukończeń i ostatnie 20/20. Ewaluacja 2/2: 45,24 s oraz 44,06 s.
Checkpoint oraz W&B sprawdzone; hiperparametry pozostają bez zmian.
Szczegóły i ograniczenia w [READINESS.md](READINESS.md).

PPO zatrzymał się przed pierwszą aktualizacją na ekranie wyniku walidacji,
bez telemetrii. Dowody zachowano w poprzedniej kolejce. Aktualny wskaźnik
prowadzi do `queue-overnight-ppo-recovery-20261004`; pozostało PPO, IQN i QR
z ewaluacjami. PPO używa jawnego nowego ID `tmrl-test-v2-ppo-retry-s17`.
Pierwsze 2048 kroków i aktualizacja przeszły poprawnie. Runner przed każdym
procesem restartuje walidację przed odczytem ramek i zamyka swój kontroler.
To naprawa startu kolejki; zamrożonych plików `.py` nie zmieniono.
Limit nadal 2 h 15 min/pilot, zapis najpóźniej 13:50 Europe/Warsaw.
Ukończonych DSAC i TQC nie powtarzamy.

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
w głównym repozytorium Jakuba. Plan po audycie używał `queue-overnight-dsac-ab-20261004`;
po awarii startu PPO zastąpiła go kolejka odzyskiwania opisana wyżej;
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
