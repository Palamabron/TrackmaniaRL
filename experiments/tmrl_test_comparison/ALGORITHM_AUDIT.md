# Audyt SD-SAC/PPO i dodatkowy SAC — 2026-10-04

## Aktualny wynik i blokada środowiska — 5 października 15:29 Warsaw

Ta aktualizacja zastępuje poniższe historyczne informacje o działającym PPO
i oczekujących procesach. PPO ukończył diagnostyczny uczony prefix cp70:
143360 kroków / 70 aktualizacji, finite i zgodny fingerprint; to nie jest pełny trening.
Dziesięć ocen dało **3/10 met**, medianę 55,34 s wyłącznie ukończonych prób.
Wszystkie pomiary timingu 6681/6681 są ważne, max 60 / p99 50 ms, bez błędów;
10778 pominiętych ramek, max 5. Timing treningu poprawił się do max 70 ms.
Skuteczność jazdy nadal nie przechodzi progu 8/10; krótszy czas trzech finisherów
nie dowodzi poprawy polityki względem wcześniejszego 8/10. Nie odblokowano pełnego startu.

QR przejął kolejkę o 15:07:14, lecz preflight zakończył się o 15:07:31:
po resecie nie otrzymano ramki telemetrii w 10 s. **Nie powstał learner, checkpoint
ani katalog treningu QR.** Jego procesy i guard zamknęły się normalnie, bez forcekill.
Oczekujący SD-SAC beta 0,005 prawidłowo przerwał przejęcie po awarii QR i również
nie rozpoczął treningu. Poprzedni SD-SAC pozostaje 0/10 i full BLOCKED.

Osobny ograniczony probe połączenia dopiero po resecie też zakończył się timeoutem.
Pięć testów kontraktu z atrapami przeszło; nie są dowodem usunięcia rzeczywistej awarii.
OpenPlanet potwierdza właściwy UID, ale `confirm_ready` zwraca `player_not_ready`.
Okno gry pokazuje przejazd bez HUD-u; dostępne próby wejścia do menu nie przywróciły
lokalnego gracza. Poproszono użytkownika o ponowne uruchomienie walidacji mapy.

Dowody są w `artifacts/tmrl-test-comparison/qr-preflight-recovery-20261005/`
(`recovery-status.json`, `session-state.json`, `probe.log`, archiwum pierwotnej awarii).
Wskaźnik active-queue nadal opisuje zakończoną awarią QR, a nie żywy kontroler;
zawsze czytaj status kolejki. Wszystkie obserwowane procesy zamknięto.
Nie uruchamiaj ponownie użytych runnerów ani zakończonych etapów. Ewentualne wznowienie
wyłącznie pozostałego QR wymaga osobnego jawnego recovery, gotowej telemetrii,
braku nowego STOP i wolnego mutexu, z zachowaniem pierwotnego **SAVE 18:27:14 /
HARD 18:37:14 Warsaw**. Limit nie zaczyna się ponownie od recovery.
Nowa rezerwacja SD-SAC musi wskazywać rzeczywistego poprawnie zakończonego poprzednika.
Cel dalszej naprawy SD-SAC i monitor ACTIVE pozostają obowiązujące; żadnych automatycznych
miesięcznych startów, zmian wspólnej nagrody ani aktualizacji zamrożonych źródeł.


## Dalsza naprawa SD-SAC — 5 października 13:33 Warsaw

Użytkownik polecił: „No to poprawiaj SD SAC tak długo aż będzie sensowny”.
Nadzór pozostaje ACTIVE również po samym PPO/QR, jeśli SD-SAC nie spełni bramki.
Ostatni SD-SAC nadal ma **0/10 met** i niepełny budżet; pełne treningi są zablokowane.

Audyt CPU zgodnego checkpointu na 1024 stanach wykazał, że przy beta 0,5 kara
utrzymująca entropię zachowania znosi niemal cały gradient preferencji wartości
(cosinus −0,9295; udział zniesiony 1,0059). To lokalna diagnoza, nie dowód błędu
matematycznego całego algorytmu. Nowa hipoteza zmienia tylko beta **0,5 → 0,005**;
wspólna nagroda, model, target entropy 0,8 i budżet 145408 pozostają takie same.
Kod dodaje diagnostykę prawdopodobieństw akcji i zgodności z krytykami oraz
usuwa zbędny graf krytyków z kroku aktora, zachowując cel i gradient aktora.

Nowy pilot faktycznie oczekuje w `queue-sd-sac-anchor005-20261005`:
**launcher 48368 / waiter 57588**, created_time 1791199959.0079837, bez kontrolera
i `launch.json`. `sd-sac-pending-queue.json` wskazuje rezerwację; właściwy stan
odczytuje się z kolejki. Frozen runtime `tmrl-sd-sac-anchor-runtime` ma źródła
`4706a06b0eea5ba3fe0d2c6aa1ad641ed29aca84`, opublikowane atomowo na obu branchach.

Kolejność pozostaje **PPO → QR → nowy SD-SAC**. PPO działał o 13:33 online:
49152 kroki / 24 pełne aktualizacje rolloutu, finite, bez awarii.
Terminy PPO i QR oraz ich zamrożone źródła są bez zmian. SD-SAC przejmuje dopiero
po normalnym końcu QR, pełnym rozliczonym checkpointcie QR, 30 ocenach, zamknięciu
procesów i guardu, braku STOP i wolnym mutexie. Pasywne oczekiwanie ma limit
**20:09 Warsaw**; nie uruchamia learnera. Po faktycznym starcie SD-SAC:
trening maks. 10800 s, 10 greedy maks. 2100 s, całe zadanie maks. **4 h**,
SAVE 600 s przed HARD. Właściwe daty pojawią się w jego `launch.json`.

Przeszło **106 testów uczenia, 20 testów nadzoru, 42 schematy**, Ruff, mypy
zmienionego źródła i standardowy CPU update/zstd roundtrip rzeczywistej kompozycji
GNN / 78 akcji. To dowody poprawności technicznej, nie nowy wynik jazdy.
Bramka pozostaje: pełny budżet, drained/accounted credit, finite/fingerprint/SHA,
10 kompletnych ważnych prób, **co najmniej 8/10 met**, max 100 ms, brak błędów,
raport pominiętych ramek. Nieudany wynik zachowujemy i diagnozujemy kolejną
uzasadnioną hipotezę w osobnym ograniczonym świeżym pilocie; bez automatycznych
pełnych treningów i bez deklaracji globalnej optymalności lub kwalifikacji 3 seedów.

Szczegóły i ograniczenia: [SD_SAC_ITERATIVE_REPAIR_20261005.md](SD_SAC_ITERATIVE_REPAIR_20261005.md).
Poniższa sekcja z 12:50 zachowuje wcześniejszy wynik i dowody.

## Nowy wynik SD-SAC i przejęcie QR — 5 października 12:50 Warsaw

Świeży SD-SAC target0,8 / beta0,5 / behavior nie zaliczył bramki: **0/10 met**,
średnio **3,552% trasy**. Wszystkie 10 prób mają ważny timing, 1961/1961 pomiarów,
max/p99 50 ms, brak błędów kontrolera i telemetrii; 2440 pominiętych ramek,
maksimum 5. Nie ma potwierdzonej poprawy skuteczności jazdy. Pełny SD-SAC
pozostaje zablokowany, generator i konfiguracje pełnych treningów bez promocji.

Pilot zakończono przez limit czasu o 12:44:29 Warsaw: **135406/145408 kroków**,
30775 aktualizacji, credit576,5, earned=accounted31351,5. Checkpoint jest finite
z potwierdzonym fingerprintem/SHA, ale budżet jest niepełny i credit nie został
wyczerpany. To ograniczenie testu, nie pełny ukończony trening. SHA checkpointu:
`6fdab80112a7e27a5bfd65cd98e01eb20297f647b4b7258045ea726e82154175`.
Dowody: `queue-ppo-sd-sac-repair-20261005/sd-sac-completion.json`,
`eval-sd-sac-evaluation.json`, `sd-sac-repair-decision.json` oraz
`tmrl-repair-diag-sd-sac-s17-benchmark-20261005T104448532426/evaluation.json`.

PPO rozpoczął świeży prefix o **12:47:13 Warsaw**, PID54168, W&B `yygy62p7` online.
Oceniamy zachowany pełny uczony cp70/143360 i 10 przejazdów zgodnie z protokołem.
SAVE16:19/HARD16:29 poprzedniej fazy pozostają bez zmian.

Przed rozpoczęciem QR wykryto dodatkowy błąd pomocnika przekazania kolejki:
czytał `sd-sac-evaluation.json` / `ppo-evaluation.json`, choć poprzednik zapisuje
`eval-sd-sac-evaluation.json` / `eval-ppo-evaluation.json`. Zatrzymano wyłącznie
pasywny pomocnik, przed jakimkolwiek etapem QR, zachowano snapshot w
`passive-wait-handoff-repair-02` i poprawiono nazwy odczytu. Nowa regresja
odtworzyła błąd; po poprawce **31 testów nadzoru** przeszło, w tym rzeczywisty
kontrakt nazw i odrzucanie niepełnego prefixu / brakujących prób / niefinite cp.
Ruff helperów i validate-only planu przeszły.

QR ponownie oczekuje: **launcher8384 / waiter55608**, bez kontrolera i bez
`launch.json` QR. `passive-handoff-recovery.json` i `pending-queue.json` wskazują
nową tożsamość. Źródła QR c4ec36a0 i SD-SAC/PPO266e2629 bez zmian; poprzednik nie
był restartowany. Warunki przejęcia, deadline oczekiwania16:34, własny limitQR
3h30 od rzeczywistego startu i bramki29/30 / mediana≤56,915s pozostają niezmienione.
Matematyczna poprawka QR nadal wymaga świeżego wyniku w grze. Monitor ACTIVE.

Poniższe sekcje zachowują wcześniejsze stany i dowody.

## Przywrócone oczekiwanie QR — 5 października 12:21 Warsaw

Pomocnik oczekujący QR zakończył się o 12:09 z `PermissionError` podczas odczytu
`status.json` poprzedniej kolejki. QR nie otworzył kontrolera, nie rozpoczął
treningu ani oceny. Zachowano pierwotny błąd, logi, rezerwację i helpery w
`queue-qr-repair-20261005/passive-wait-recovery-01`; zapis w
`passive-recovery.json` potwierdza zamknięcie starego pomocnika i brak etapów QR.

Poprawiono tylko odczyty zewnętrznego pomocnika QR i jego przyszłego guardu:
ponawianie trwa najwyżej 5 s, a trwały błąd nadal przerywa pracę. Wszystkie
26 testów CPU nadzoru przeszło, w tym 5 nowych regresji: rzeczywista wyłączna
blokada pliku Windows, ograniczony trwały błąd uprawnień, przerwa podmiany pliku,
odrzucenie uszkodzonego JSON i niedozwolonego długiego ponawiania. Walidacja
planu i Ruff helperów przeszły. Poprzednie 32 testy źródeł i próba QR64 update /
zstd roundtrip pozostają zachowanymi dowodami, nie nowym wynikiem jazdy.

Oczekiwanie przywrócono: launcher **60600**, runner **60380**,
`waiting_for_predecessor`, pusty `runner.err`, bez `launch.json` QR.
`pending-queue.json` wskazuje nową tożsamość; aktywna kolejka pozostaje SD-SAC/PPO
z runnerem 61144 i guardem 3356. Nie zmieniono jej źródeł, helperów ani etapów.
Zamrożone runtime QR c4ec36a0 oraz SD-SAC/PPO 266e2629 pozostały bez zmian.

Zakres i warunki przejęcia są niezmienione: wszystkie cztery etapy poprzednika,
pełny uczony prefix PPO i 10+10 ocen, zamknięte procesy, wolna wspólna blokada,
brak nowego STOP. Oczekiwanie kończy się najpóźniej o 16:34 Warsaw. QR nadal ma
własne 3 godz. 30 min od rzeczywistego startu, SAVE 10 min przed HARD i wcześniej
zapisane bramki 29/30 met / mediana ≤56,915 s. Wynik nowego QR w grze nadal
oczekiwany. Nadzór pozostaje ACTIVE; pełnych treningów nie uruchomiono.

Poniższe sekcje zachowują wcześniejsze stany i dowody.

## Aktualny stan — QR-DQN dołączony po PPO, 5 października 12:05 Warsaw

Użytkownik polecił poprawić QR-DQN i dodać go do kolejki, następnie zezwolił
na późniejsze zakończenie testów, także po19:00, przed prawdziwymi treningami.
Poprawka QR jest opublikowana: **c4ec36a0b6d2eaf948c9eb24a783e344b81c1314**.
Nowy QR używa osobnego frozenruntime `tmrl-qr-repair-runtime`; aktualne
SD-SAC/PPO266e2629 oraz starsze runtime pozostają bez zmian.

Faktycznie dodany etap oczekujący: `queue-qr-repair-20261005`, launcher28636,
runner61196, status `waiting_for_predecessor`, bez kontrolera i bez `launch.json`.
`pending-queue.json` wskazuje QR; `active-queue.json` do zakończenia PPO wskazuje
bieżącą kolejkę SD-SAC/PPO. QR przejmie wskaźnik dopiero po wszystkich czterech
etapach, potwierdzonych wynikach, zamknięciu ich procesów/guardu i sprawdzeniu
wspólnej blokady. Nie uruchamia drugiego kontrolera ani nie ponawia poprzednika.

QR: świeży145408/seed17, max8100s, potem30greedy/max2700s. Nowa faza ma osobny
limit3h30 od faktycznego startu QR i SAVE10min przed HARD. Konkretne godziny
będą dopiero w QR `launch.json`/`effective-deadline.json`;16:29 pozostaje limitem
poprzedniej fazy. Jej prawidłowe zamknięcie nie kończy jeszcze autoryzowanego QR.
Nowy STOP, awaria lub niepełne PPO zatrzymują automatyczne przejęcie.

32testy źródeł +21testów CPU nadzoru i bramki przeszły, Ruff i mypy zmienionego
źródła przeszły. Pełna konfiguracja kompozycji QR64 przeszła standardowy validator
na CPU: syntetyczny update i zstd checkpoint roundtrip, bez gry, kontrolera i
nowego W&B. Bramka QR jest z góry: pełny/drained/finite/fingerprint/SHA pilot,
30ważnychprób/max100ms/noerrors/skips, >=29/30met i mediana<=56,915s. Wynik
jazdy nadal oczekiwany; matematyczna poprawka nie gwarantuje poprawy polityki.

Monitor ACTIVEco15min obejmuje również oczekujący QR. Raport końcowy i PAUSED
nastąpią po wszystkich autoryzowanych etapach lub ich zatrzymaniu/awarii/limicie.
Pełnych treningów nie uruchamiamy; QR, PPO i SD-SAC nie otrzymują deklaracji
optymalnych HP lub gotowości trzech seedów bez rzeczywistych wyników.
Protokół, analiza ograniczeń i punkt odniesienia:
[QR_REPAIR_20261005.md](QR_REPAIR_20261005.md).

Poniższe sekcje zachowują wcześniejsze stany i dowody.

Aktualna oddzielna kolejka naprawcza wystartowała 5 października10:29Warsaw: `queue-ppo-sd-sac-repair-20261005`, nowy frozenruntime266e2629. Świeży SD-SAC target0,8/beta0,5/behavior145408 +10greedy, następnie PPO.01 prefix143360uczonych (STOP145408, LRhorizon2048000) +10greedy. Nowa faza ma limit6h, SAVE16:19/HARD16:29Warsaw; te godziny są nadrzędne dla nowych testów po bezpośrednim przedłużeniu przez użytkownika. Właściwy wskaźnik: `artifacts/tmrl-test-comparison/active-queue.json`; runner61144, niezależny guard3356, W&B `wcsd62q4` online. 203testy kodu +21testów guardówCPU przeszły. Stary fixturepoczątkowegoplanu odłożono: historyczna retencja usunęła cp659; jego nowy start jest zabroniony. Pełny SD-SAC nadal zablokowany, wspólna nagroda bez zmian, bez automatycznych miesięcznych treningów. Live wynik nowych poprawek jest jeszcze w toku.


## Zakończenie nocy i naprawy po przedłużeniu — 5 października

Nocna kolejka ukończyła wszystkie etapy 09:26:36 Warsaw; ostatni QR **26/30 met**,
mediana56,915s/średnia57,124s, max50ms, poprawny timing i brak błędów.
Użytkownik następnie przedłużył pracę poleceniem „Możesz robić dłużej niż do 10
 tylko spraw by PPO i DSAC poprawnie działało”. Wcześniejsze terminy są historią
zakończonej kolejki; nowe ograniczone testy mają własny jawny limit.
Reset nowego kodu zaliczony w grze; poprawki rozgrzewki/timingów PPO i stabilizacji
SD-SAC są testowane przed świeżymi pilotami. Pełny SD-SAC pozostaje zablokowany,
PPO zachowuje entropy0,01. Nagroda pozostaje wspólna; automatycznych miesięcznych
treningów nie uruchamiamy. Pełne wyniki, dowody, ograniczenia i nowy protokół:
[REPAIR_PPO_SD_SAC_20261005.md](REPAIR_PPO_SD_SAC_20261005.md).

Starsze sekcje poniżej opisują kolejne historyczne stany; powyższy stan jest bieżący.

## SAC 30 prób — 5 października, 09:10 Europe/Warsaw

Zachowany stary cp33854 na runtime d0dfe645 ukończył ocenę: **30/30 met**,
średnia **44,366 s**, mediana **44,500 s**, najlepsza **42,500 s**.
Wszystkie 30 prób mają ważny timing: 26 627/26 627 pomiarów, max/p99 **50 ms**,
brak błędów telemetrii/kontrolera. Pominięte ramki **8 021**, maksimum 5.
Zachowujemy pozytywny baseline SAC. To ocena jednej polityki seed17, nie dowód
powtarzalności treningu na trzech seedach ani osiągnięcia celu 37 s.
Dowód: `tmrl-overnight-diag-sac-s17-benchmark-20261005T063406463907/evaluation.json`;
SHA cp `620f9b1aaabb1afda5355b82ec7a1b71412262df6299e37de0bb3aae76f0ea3e`.
W&B `wjlsmn59` finished. Ostatnia ocena QR rozpoczęła 08:57:38 Warsaw, PID56000;
09:10 ukończono 13 prób, 12 met — wynik częściowy. Kampania trwa.
SAVE 10:24 / HARD 10:34 bez zmian; pełnych treningów nie uruchomiono.

## TQC 30 prób — 5 października, 08:40 Europe/Warsaw

Zachowany stary cp33858 na runtime d0dfe645 ukończył ocenę:
**29/30 met**, średnia **44,384 s**, mediana **44,300 s**, najlepsza **43,790 s**.
Wszystkie 30 prób mają ważny timing: 26 222/26 222 pomiarów, max **60 ms**,
p99 **50 ms**, brak błędów telemetrii/kontrolera. Pominięte ramki **8 080**,
maksimum 6. Zachowujemy pozytywny baseline TQC. Ocena potwierdza tę politykę
seeda17, nie powtarzalność treningu na trzech seedach ani osiągnięcie celu 37 s.
Dowód: `tmrl-overnight-diag-tqc-s17-benchmark-20261005T061051859378/evaluation.json`;
SHA cp `6dda21d2d3d5ee119919d66741517f608b2b9e12e63f8764fe4d3ce8aff29a7f`.
W&B `4twuxhg7` finished. SAC rozpoczął 08:34:03 Warsaw, PID52608,
W&B `wjlsmn59`; QR pozostaje w kolejce. Kampania trwa.
SAVE 10:24 / HARD 10:34 bez zmian; pełnych treningów nie uruchomiono.

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
SAVE 10:24 / HARD 10:34 bez zmian; pełny SD-SAC nadal zablokowany.

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

## Wynik SD-SAC — 5 października, 03:10 Europe/Warsaw

Pilot celu entropii 2,0 / beta 0 zakończył **145 487 kroków / 33 871 aktualizacji**.
Końcowy cp33871 ma skończone tensory, zgodny fingerprint i rozliczony kredyt
**0,75** (`earned = accounted = 33 871,75`). Ocena zakończona: **0/10 met**,
postęp 4,24–5,17%, średnio 4,42%. Wszystkie pomiary czasu ważne, max/p99 50 ms,
brak błędów telemetrii/kontrolera; 651 pominiętych ramek, maksimum 5.
Warunek minimum 8/10 met NIE został spełniony: **pełny SD-SAC nadal zablokowany**,
hipoteza diagnostyczna nie zostaje promowana do konfiguracji seedów 17/29/43.
Poprawny zapis i sprawny pomiar nie oznaczają skutecznej polityki greedy.
Dowody: `queue-overnight-tuning-20261005/dsac-completion.json` oraz
`tmrl-overnight-diag-dsac-e200-b0-s17-benchmark-20261005T005546181914/evaluation.json`
w `artifacts/tmrl-test-comparison`. W&B trening `2fslk8zh`, ocena `vepn4pyj`.

To wynik częściowy kampanii. Świeży PPO baseline ruszył 02:58:36 Warsaw;
pozostałe etapy prowadzi istniejący runner. Nagroda i zamrożone runtime bez zmian.
Termin zapisu 10:24, twardy koniec 10:34 pozostają nadrzędne.


Wspólna nagroda pozostaje bez zmian. TQC nauczył się kończyć mapę w tym
samym protokole, a PPO także ją kończy. Audyt dotyczy polityk, temperatury,
akcji i aktualizacji, bez modyfikowania źródeł działającego treningu.

## Aktualizacja audytu — 2026-10-04, około 17:10 Europe/Warsaw

W osobnym checkoutcie `tmrl-training-fixes` poprawiono inicjalizację PPO.
`PpoGaussianActor._initialize_weights` nadpisywał ortogonalnymi wagami
celowo zerowe projekcje adapterów context, spatial i recovery encodera V6.
Przed poprawką ich normy po konstrukcji PPO wynosiły odpowiednio
19,596 / 19,596 / 11,314 zamiast zera. Adaptery miały więc niezerowy wpływ
już przed pierwszą aktualizacją, wbrew założeniu ich inicjalizacji.

Poprawka zachowuje te zerowe projekcje oraz standardową inicjalizację
pozostałych warstw. Porównanie CPU dla seed 17 z wcześniejszym kodem
wykazało różnicę dokładnie w trzech tensorach:

- `actor.encoder.context_adapter.3.weight`;
- `actor.encoder.spatial_adapter.output_projection.weight`;
- `actor.encoder.recovery_adapter.3.weight`.

Wszystkie pozostałe parametry modelu, w tym krytyka, oraz stan RNG pozostały
identyczne. Stary checkpoint pilota załadował się z pełną zgodnością kluczy;
maksymalna różnica deterministycznej akcji przed i po poprawce wyniosła 0,0.
Przeszły 64 różne testy CPU obejmujące PPO, aktorów, V6 i runtime oraz
kontrola Ruff i formatowania. Testy regresji sprawdzają także, że zachowane
zerowe projekcje nadal otrzymują niezerowy gradient uczenia.

To potwierdzony błąd inicjalizacji, **niedowiedziona przyczyna wolniejszej
jazdy starego PPO**. Poprawka wpływa na nowe treningi od zera; ewaluacja
starego checkpointu nie sprawdza jakości tej nowej inicjalizacji. Aktualny
kandydat PPO zachowuje hiperparametry baseline, w tym współczynnik entropii
0,01 i pełny harmonogram 2 048 000 kroków. W nowym, zatwierdzonym budżecie
3 godzin testów jazdy priorytetem jest diagnostyczny pilot SD-SAC; nie należy
opisywać nowej inicjalizacji PPO jako zweryfikowanej długim pilotem w grze.

## Discrete SAC: nadal niegotowy

Wariant bez kary entropii zakończył 145 412 kroków i 33 853 aktualizacje:
0/246 met treningowych i 0/3 w ewaluacji. Wyłączenie wcześniej wykrytego
hamowania gradientu przez karę nie rozwiązało problemu jazdy.

Na 256 stanach losowo wybranych z całego końcowego replayu:

| Pomiar | Wynik |
| --- | --- |
| Cel entropii | 3,485 nats = 0,8 ln(78) |
| Średnia entropia aktualnej polityki | 3,365 nats, około 29 efektywnych akcji |
| Średnie prawdopodobieństwo pełnego gazu bez hamowania | 29,2% |
| Średnie prawdopodobieństwo pełnego hamulca | 19,3% |
| Średnie prawdopodobieństwo krótkiego brake-tap | 31,7% |
| Alpha | 0,02175 |
| Clipping krytyka blokujący gradient na próbce | 0% i 0,39% |
| Zgodność argmax aktora z argmax średniego Q | 23,8% |
| Średnia strata Q przez wybór argmax aktora zamiast argmax Q | 0,02455 |

Kierunek aktualizacji alpha oraz uczenie toy bandyty zostały sprawdzone.
Nie znaleziono odwróconego znaku temperatury ani dominującego blokowania
krytyka przez clipping. Należy jednak skorygować wcześniejszą interpretację
zgodności argmax: przy ustalonym Q, dodatnim alpha i wyłączonej dodatkowej
karze optimum celu aktora to `softmax(Q / alpha)`, które zachowuje argmax Q.
Sama entropia nie wyjaśnia więc obserwowanej rozbieżności aktora i krytyka.
Może ona sygnalizować niedopasowanie uczonego aktora do zmieniającego się Q;
ten pomiar nie ustala przyczyny. Różnicy Q = 0,02455 nie można automatycznie
nazwać małą: względem alpha = 0,02175 wynosi około 1,13. Postać optimum
wynika z celu aktora przedstawionego w równaniach 7–8 pracy
[Revisiting Discrete SAC](https://arxiv.org/html/2209.10081#S3).

Obniżenie celu entropii pozostaje hipotezą do testu. Tabela ma
13 akcji pełnego gazu bez hamowania; rozkład ograniczony do nich ma entropię
najwyżej ln(13) = 2,565. Przy entropii pojedynczego stanu równej celowi 3,485
nawet maksymalnie równomierny podział w obu grupach wymaga co najmniej 23,4%
masy poza tą grupą. To ograniczenie matematyczne, nie dowód, że hamowanie
jest zawsze złe; regulator działa na średniej, a poszczególne stany mają
różne entropie. Obserwowane 29,2% masy w grupie pełnego gazu wskazuje jednak,
że obecna polityka nadal często odpuszcza gaz lub hamuje.

Lokalny learner jest wariantem **SD-SAC-inspired**: kara porównuje bieżącą
entropię z entropią aktora target aktualizowanego metodą Polyaka. Tymczasem
[sekcja 5.1 pracy SD-SAC](https://arxiv.org/html/2209.10081#S5.SS1)
opisuje entropię polityki zachowania zapisaną razem z przejściem w replayu,
a [referencyjny `discrete_sac.py`](https://github.com/coldsummerday/SD-SAC/blob/main/src/libs/discrete_sac.py)
w `learn()` pobiera `old_entropy` z batcha i stosuje karę MSE względem niej.
To konkretna różnica definicji kotwicy, nie wierna implementacja tej części
SD-SAC. Przy `entropy_penalty_coefficient: 0.0` różnica kotwicy nie wpływa
na gradient celu; nie wyjaśnia sama niepowodzenia wariantu beta = 0.

Eksploracja SD-SAC jest natywnym próbkowaniem z rozkładu kategorycznego aktora;
ewaluacja używa jego argmax. Logowana przez infrastrukturę wartość epsilon
nie dodaje w tej ścieżce losowych akcji epsilon-greedy i pozostaje nieaktywna.
Nie należy interpretować jej spadku jako zmniejszania eksploracji SD-SAC.

Następny test: `configs/diagnostic/sd-sac-entropy200-beta000-s17.yaml`:
cel 2,0 nats, kara 0,0, wszystkie inne ustawienia, akcje, model i nagroda bez
zmian. Na moment aktualizacji około 17:10 konfiguracja jest przygotowana
do testu, ale **nie jest zakwalifikowana jako pełne ustawienie Borysa**.
Niższy cel 2,0 i beta = 0 są hipotezą, nie potwierdzoną naprawą jazdy.
Sam pomiar CPU nie rozstrzyga przyczyny niepowodzenia; potrzebny jest
kontrolowany pilot i ewaluacja przed ewentualnym przeniesieniem ustawień
na pełne seedy 17/29/43.

## PPO: uczy się, lecz pilot ma wolniejszą jazdę

Końcowy checkpoint `update-00000071.pt`: 145 408 kroków, 71 aktualizacji
rolloutów i **4280 kroków Adam**, nie tylko 71 kroków optymalizatora.
W&B treningu i ewaluacji ma stan `finished`. Dwa przejazdy bez eksploracji:
**58,27 s i 59,13 s**, średnia 58,70 s. TQC w swoich dwóch przejazdach miał
44,65 s: różnica 14,05 s (31,5%) w tej małej próbie, nie ranking algorytmów.

Pełne 71 plików rolloutów zawiera 13 potwierdzonych met treningowych:
best 87,27 s, mediana 97,86 s. Pozostałe znaczniki: 34 slow-progress,
39 no-progress oraz 71 sztucznych granic rolloutów. Skrócony `train/episode`
zapisuje tylko ostatni epizod rolloutu i nie nadaje się do liczenia wszystkich
met. Wcześniejszy brak met w tych logach nie oznacza braku uczenia PPO.

W końcowych 10 rolloutach stochastycznych gaz średnio 0,718, hamulec 0,365;
przez 54,7% kroków oba przekraczały 0,2. Końcowe odchylenia pre-tanh polityki
wynosiły 0,978 / 0,891 / 0,934, więc eksploracja w treningu nadal była duża.
Nie należy przenosić tych wartości bezpośrednio na deterministyczną jazdę.

Osobny pomiar obu końcowych modeli na tych samych 256 stanach replayu TQC:

| Deterministyczna akcja | PPO | TQC |
| --- | --- | --- |
| Średni gaz | 0,752 | 0,942 |
| Średni hamulec | 0,336 | 0,137 |
| Gaz i hamulec jednocześnie >0,2 | 73,4% | 10,2% |

To porównanie kontrfaktyczne na wspólnych stanach, nie zapis rzeczywistych
akcji ewaluacyjnych PPO. Wskazuje na zachowawczą politykę gazu i utrzymujące
się hamowanie jako mechanizm wolniejszego tempa, ale nie izoluje przyczynowo
ich wpływu na czas końcowy.

Learning rate pilota spadł z 0,0003 do 0,00000423; KL zatrzymał wcześniejsze
epoki w 46/71 rolloutów. To działające zabezpieczenie PPO, nie awaria.
Nie porównywać licznika rolloutów z licznikiem minibatchy innych algorytmów.
W pełnej konfiguracji 2 048 000 kroków ten sam harmonogram wygasza LR dużo
wolniej: przy około 145 tys. kroków pozostaje około 0,000279. Pilot nie dowodzi,
że pełny PPO utknie na obecnym czasie. Nie zmieniamy baseline hiperparametrów
na podstawie dwóch przejazdów; najpierw dłuższa obserwacja kontrolowana.

Nie znaleziono błędu znaków w clipped-policy loss, bootstrapie GAE lub korekcie
log-probability pre-tanh. Finalne parametry są skończone. Jest ograniczenie
czasowe: w jednej ewaluacji maksymalny odstęp zegara wyścigu wyniósł 140 ms,
choć p99 obu prób wynosi 50 ms; w drugiej maksimum 50 ms. Liczniki pominiętych
ramek są niezerowe (1556 i 1544). Przed pełnym startem Kuby wymagany lokalny
test i ponowny pomiar odstępów; ta diagnostyka nie jest końcowym gate 30 prób.

[Trening PPO](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/6mmbtw48),
[ewaluacja PPO](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/78ptxnew).

## Continuous SAC: pilot zakończony

Końcowy checkpoint `distributed-update-00033854.pt` ukończył **2/2**
przejazdów bez eksploracji: **43,78 s i 44,75 s**, średnia **44,265 s**.
Źródłem wyniku jest `evaluation.json` przebiegu
`tmrl-test-v2-sac-s17-benchmark-20261004T133913799286` w lokalnych artefaktach.
To wynik małego pilota, nie globalny ranking ani potwierdzenie wyższości SAC
na trzech seedach. Wspólna nagroda i model nie zostały na tej podstawie zmienione.

Historyczny plan kolejki, już wykonany: użytkownik zatwierdził rozszerzenie
czasu do **16:15 Europe/Warsaw**. SAC miał wystartować po IQN i QR od zera,
seed 17, na 145 408 kroków lub 2 h 15 min, z dwoma przejazdami ewaluacji.
Model, ciągłe akcje, nagroda, geometria, UTD 0,25 i batch 256 były zgodne
z TQC. Kolejka `queue-continuous-sac-20261004` czekała na zakończenie
poprzedniej i wolny kontroler, respektowała STOP oraz awarię poprzedniej,
z granicą zapisu 16:05. Ten opis nie oznacza obecnie oczekującego zadania
ani nie określa nowego trzygodzinnego budżetu diagnostycznego.

Raporty i skrypty CPU są lokalnie w `artifacts/tmrl-test-comparison/algorithm-audit-20261004`.
W pierwszym audycie źródła `.py` biblioteki i encodera pozostawały zgodne
z `378f9c6a`; późniejsza poprawka PPO jest opisana w aktualizacji powyżej.
Ówczesna weryfikacja obejmowała 26 testów PPO/GAE/aktorów Gaussa, schema
SAC, CPU update i checkpoint round-trip, pełne seedy 17/29/43 oraz parser
launchera. Sam audyt kodu i pomiary CPU nie uruchamiały dodatkowego
kontrolera gry.

## Źródła koncepcyjne

Algorytmy różnią się sposobem ponownego wykorzystania danych; nie zrównujemy
liczników aktualizacji bez uwzględnienia rolloutów, minibatchy i epok.
[Spinning Up: algorytmy](https://spinningup.openai.com/en/latest/user/algorithms.html).
Dobór celu entropii w discrete SAC jest przedmiotem osobnych badań;
[Target Entropy Annealing](https://arxiv.org/abs/2112.02852) i
[Revisiting Discrete SAC](https://arxiv.org/abs/2209.10081) nie zastępują
kontrolowanego testu na tej mapie. Powyższe diagnozy pochodzą z lokalnych
metryk, kodu i checkpointów, a nie z przeniesienia wyników tych prac.
