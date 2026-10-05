# Podział eksperymentów

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


## Aktualizacja — 5 października, kampania nocna

Po wyraźnym wznowieniu użytkownika działa `queue-overnight-tuning-20261005`.
Budżet 10 godzin od początku pracy 00:34, zapis 10:24, twardy koniec 10:34 Warsaw.
Runner 37100 sam prowadzi etapy; nie uruchamiać kolejnego kontrolera ani pełnych
treningów. Poprzednie STOP pozostają dowodem, nowe STOP nadal zatrzymuje.
Aktualny plan i warunki doboru parametrów: [TUNING.md](TUNING.md).
Przydziały pozostają: Jakub IQN/QR, Borys SD-SAC, Kamil TQC, Kuba P. PPO,
SAC bez przydziału. Pełne trzy seedy dopiero z końcowego wspólnego commita,
od zera, po lokalnej kalibracji i smoke; nie wznawiać pilotów na nowym kodzie.

## Historia: kolejka z 4 października 17:28, zatrzymana na polecenie użytkownika

Kod zespołu opublikowany na obu branchach: **8f440075**. Nowy pilot korzysta
z osobnego, czystego i zamrożonego `tmrl-tuning-runtime` na tym commicie.
Stare IQN/PPO będą oceniane na zachowanym `tmrl-algorithm-runs` (`d0dfe645`,
źródła Python `378f9c6a`), bez przenoszenia checkpointów między wersjami.

Kolejka `queue-tuning-20261004` wystartowała **17:27:56 Europe/Warsaw**.
Termin zapisu **20:17:56**, twardy koniec **20:27:56**. To zatwierdzone nowe
3 godziny łącznie, nie przedłużanie poprzedniej kampanii. Wskaźnik
`artifacts/tmrl-test-comparison/active-queue.json` wskazuje tę kolejkę.
SD-SAC `tmrl-tuning-dsac-entropy200-beta000-s17` działa, W&B
[o3aknhmz](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/o3aknhmz)
potwierdzony online/running. O 17:30 zapisano 1943 kroki w fazie warmup,
ważny timing ostatniego epizodu (p99 50 ms, max 60 ms), brak błędu telemetrii.
To kontrola uruchomienia, nie wynik uczenia ani kwalifikacja SD-SAC.

Następnie planowane są 10 ocen SD-SAC, 10 IQN i 5 PPO w pozostałym czasie.
Warunki promocji SD-SAC oraz sprawdzone ustawienia opisuje [TUNING.md](TUNING.md).
Monitor działa co 5 minut i ma zakończyć pracę po raporcie tej kampanii.
Pełnych treningów nie uruchomiono. Końcowy dobór SD-SAC pozostaje otwarty do
wyniku jazdy; jego pełne uruchomienia są nadal zablokowane.


## Nowe przygotowanie i testy — 2026-10-04 po 17:00

Po zakończeniu poprzedniej kampanii użytkownik zatwierdził naprawy oraz
**do 3 godzin łącznie nowych testów w grze**. Aktualne decyzje o parametrach,
kolejność prób, poprawki PPO i warunki wyboru SD-SAC opisuje [TUNING.md](TUNING.md).
Pełne treningi pozostają ręczne; SD-SAC nadal jest zablokowany do wyniku nowego
pilota. Stare checkpointy zachowują swój zamrożony runtime. Poniższy raport
15:41 i starsze sekcje dokumentują zakończoną poprzednią kampanię, nie nową kolejkę.

## Kampania zakończona — 2026-10-04, 15:41 Europe/Warsaw

Wszystkie zaplanowane piloty i krótkie ewaluacje zakończone. TQC, QR, PPO
oraz continuous SAC mają pozytywne piloty; IQN ukończył 1/2 przejazdów i
wymaga dalszej kontroli stabilności. SD-SAC pozostaje niegotowy. Pełnych
treningów nie uruchomiono automatycznie. Wyniki, timing i ograniczenia:
[READINESS.md](READINESS.md).

| Osoba | Algorytm | Warunki pełnych treningów |
| --- | --- | --- |
| Jakub | IQN i QR | każdy: 17/29/43, lokalny smoke; IQN stabilność do sprawdzenia |
| Borys | discrete SAC | zablokowane; najpierw pilot 2,0 / beta 0 i wybór ustawień |
| Kamil | TQC | 17/29/43 po lokalnej kalibracji i smoke |
| Kuba P. | PPO | 17/29/43 po lokalnym smoke i kontroli timingu |
| Bez przydziału | continuous SAC | 17/29/43 po lokalnym smoke; ręczny start odblokowany |

Aktualna decyzja przed pełnym startem: [READINESS.md](READINESS.md).
Launcher blokuje pełne SD-SAC do czasu pozytywnego testu niższej entropii. Dla Borysa przygotowano
wyłącznie test: `run_assigned.ps1 sd-sac -Pilot` (145 408 kroków, seed 17,
cel entropii 2,0, kara 0,0). Po nim potrzebna osobna ewaluacja bez eksploracji;
skrypt nie przechodzi automatycznie do pełnych seedów.
IQN i QR zakończyły kampanię v2; nie powtarzać ich automatycznie.
Discrete SAC bez kary entropii zakończył pilot, lecz ewaluacja
dała 0/3 ukończeń (postęp 78,9%, 5,4%, 5,4%). **Borys: pełne treningi jeszcze
nie są gotowe do startu.** Przygotowano osobny, nieuruchomiony test celu
entropii 2,0; instrukcję i ograniczenia opisuje READINESS.md.
**Kamil / TQC: pilot v2 zakończony pozytywnie**, 145 433 kroki, 71/181 met
w treningu i 2/2 w krótkiej ewaluacji (45,24 s; 44,06 s). Hiperparametry
pozostają bez zmian; przed pełnym startem wymagany lokalny test i kalibracja.
**Kuba P. / PPO: ukończony pilot**, 145 408 kroków, 13 met w pełnych śladach
treningu i 2/2 w ewaluacji (58,27 s; 59,13 s). Zachowujemy baseline; przed
pełnym startem lokalny test oraz kontrola pojedynczego odstępu 140 ms.
Audyt i ograniczenia: [ALGORITHM_AUDIT.md](ALGORITHM_AUDIT.md).
**Continuous SAC: 145 416 kroków, 83/198 met, ostatnie 20/20**, ewaluacja
2/2 (43,78 s; 44,75 s), max/p99 50 ms, bez błędów. Baseline bez zmian;
nie ma jeszcze przydzielonej osoby. Dwa przejazdy nie zastępują 30 prób/seed.
Końcowy stan kolejki opisuje [NIGHT_QUEUE.md](NIGHT_QUEUE.md).
Pełnych treningów nie
uruchamiamy automatycznie po pilotach. Przed przekazaniem do długich prób
sprawdzamy każdy algorytm: aktualizacje o skończonym lossie, zmiana polityki,
ukończony budżet, poprawny zapis końcowego checkpointu, metryki w W&B,
stabilne sterowanie i brak błędów telemetryki. Pilot nie musi ukończyć mapy,
ale sam działający proces nie jest jeszcze pozytywnym wynikiem testu.

Bezpośredni reset poprawionego nowego kodu sprawdzono lokalnie po zamknięciu
kolejki: zgodny UID, telemetria i zegar 10 ms; klient i kontroler zamknięte.
To nie zastępuje lokalnego smoke jazdy na komputerze każdej osoby. Wszyscy
używają jednego nowego commita obu branchy i zapisują hash; pełny start
od zera. Stary zamrożony checkout służy tylko starym checkpointom.

## Instalacja u kolegi

Użyj brancha `codex/tmrl-algorithm-runs` w osobnym katalogu. Jest to snapshot bieżącego
kodu wraz z lokalnymi zmianami; używaj tego samego commita u wszystkich.
Nie podmieniaj go na wersję biblioteki z PyPI. Wymagany Windows, GPU NVIDIA
ze sterownikiem zgodnym z dołączonym środowiskiem CUDA, Trackmania i Openplanet.

```powershell
git clone --branch codex/tmrl-algorithm-runs https://github.com/TrackmaniaRL/TrackmaniaRL.git
cd TrackmaniaRL
```

1. Zainstaluj uv, a w katalogu repozytorium wykonaj `uv sync --group dev`.
2. Skonfiguruj Openplanet School Mode, plugin TrackmaniaRL Connect / SAC_GetData
   i wirtualny gamepad zgodnie z `readme/trackmania.md`.
3. Otwórz dołączoną mapę `my-trackmania-agent/maps/trackmaniarl-test.Map.Gbx`
   w edytorze w trybie walidacji. Geometria jest już w paczce.
4. Utwórz własny prywatny `.env` z `WANDB_API_KEY=twoj_klucz`.
   Branch nie zawiera klucza Jakuba. Konto musi mieć dostęp do projektu zespołu.
5. Ustaw w PowerShell `$env:WANDB_ENTITY = 'dsc-pjatk-warsaw'`.
   Jeśli nie masz dostępu, ustal go z Jakubem przed startem.
6. Sprawdź CUDA: `uv run python -c "import torch; print(torch.cuda.is_available())"`.
   Wynik musi być `True` dla tych konfiguracji.
7. Sprawdź połączenie: `uv run trackmaniarl track check` oraz test bez gry:
   `uv run python -m experiments.tmrl_test_comparison.check`.
8. Bez działającego treningu, na załadowanej mapie zmierz lokalne sterowanie:
   `uv run trackmaniarl track check-steering --output artifacts/tmrl-test-comparison/steering-local.json`.
   Konfiguracje wymagają tego pliku. Nie kopiuj krzywej innej osoby; po zmianie
   ustawień kontrolera zmierz ją ponownie. Patrz [NIGHT_QUEUE.md](NIGHT_QUEUE.md).

Launcher przed każdym seedem sprawdza UID, restartuje walidację i wymaga
gotowego gracza oraz telemetrii. Kończy ten kontroler przed startem treningu;
nie uruchamiaj go obok innej jazdy. Chroni to przed brakiem ramek na ekranie
wyniku poprzedniego seeda. Błąd sprawdzenia zatrzymuje kolejkę.
Launcher sprawdza także działające procesy treningu i ewaluacji oraz odmawia
startu, jeśli katalog runu już istnieje. Wznowienie checkpointu wymaga osobnego
polecenia; ponowne uruchomienie launchera nie nadpisuje istniejącej próby.
Tryb `-Pilot` uruchamia tylko seed 17 z budżetem pilota, zwykle około 2–3 h
plus restarty i uczenie; nie ma twardego limitu czasu ściennego.

Po pozytywnym lokalnym pilocie przypisanego algorytmu uruchom **jedno** polecenie:

```powershell
# Kamil:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 tqc
# Kuba P.:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 ppo
# Operator continuous SAC, dopiero po lokalnym smoke i kalibracji:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 sac
```

Każde polecenie wykonuje trzy seedy kolejno, od zera. Nie uruchamiaj dwóch
algorytmów naraz na jednej instancji gry. IQN i QR u Jakuba mają analogiczne
polecenia. Bezpieczne zatrzymanie: utwórz plik `artifacts/STOP-NAZWA_ALGORYTMU`.
Ponowne wykonanie skryptu nie wznawia checkpointów i zatrzyma się na istniejącym
katalogu runu. Po przerwaniu wznów konkretny seed według protokołu.

## Co zwrócić

Linki do trzech runów W&B oraz foldery tych runów z `artifacts/tmrl-test-comparison/`,
w tym checkpointy, manifesty i JSONL. Zachowaj hash commita, model GPU/CPU,
wersję sterownika, FPS gry i ustawienia grafiki. Sprzęt i obciążenie gry mogą
zmieniać timing sterowania, więc sprawdzamy rozkład odstępów decyzji na każdym
komputerze. Nie porównuj samego czasu ściennego bez informacji o sprzęcie.

Ocena końcowych checkpointów: 30 przejazdów według `README.md`, osobno dla
każdego seeda; najlepiej wszystkie checkpointy ocenić później na jednym komputerze.
W&B jest wspólnym podglądem metryk, lokalne pliki zachowują pełny zapis próby.
