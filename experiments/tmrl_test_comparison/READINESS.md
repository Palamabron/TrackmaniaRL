## Poprawki kodu SD-SAC po nowym poleceniu człowieka — 6 października 2026

Polecenie „to napraw to wszystko” wykonano w editable; trening, ewaluacja jazdy i nowe
piloty nadal wymagają osobnej zgody. Automatyzacja PAUSED, STOP zachowany, Full SD BLOCKED.
Naprawiono zapis tempa aktora, dodano stabilne log-softmax, osobną regulację temperatury
z opcjonalnymi granicami, kontrolę opcji/optimizerów checkpointu, jawny opcjonalny
wariant soft-Q forward-KL oraz diagnostykę błędu krytyka i zapadania polityki.
SD-SAC wymaga n_step1; poprawiono również generatory i przykład dokumentacji.
91 testów kodu CPU passed (2 długie pętle syntetyczne pominięte), generator7 ponownie
passed, Ruff i mypy passed. Nie uruchomiono żadnego nowego eksperymentu jazdy/treningu.

Odczyt istniejącego cp25112: 31 kompletnych epizodów, terminal Qmean1.6086 wobec
rzeczywistej ostatniej nagrody −2.0518 (bias3.6604, RMSE4.1004). Wagi pozostają bez zmian;
kod nie daje jeszcze dowodu naprawionej kalibracji lub jazdy. Analiza inference-only,
bez learnera/optimizer steps/kontrolera; SHA/fingerprint i frozen runtime zachowane.
Szczegóły: [SD_SAC_CODE_REPAIR_20261006.md](SD_SAC_CODE_REPAIR_20261006.md).
Poniższe „nie poprawiano algorytmu” dotyczy wcześniejszego etapu analizy; starsze
ACTIVE i zgody na autonomiczne starty pozostają odwołane.

## SD-SAC zatrzymany na żądanie człowieka — 6 października 14:08 Warsaw

Nadrzędna instrukcja: zatrzymać SD-SAC, przeanalizować poprawki, **nie uruchamiać
nowego treningu, testu jazdy, ewaluacji ani pilota bez wyraźnego nowego pozwolenia**.
Wcześniejsze upoważnienia do autonomicznych pilotów są odwołane. Automatyzacja PAUSED.

`queue-sd-sac-actorlr0009-20261006` otrzymała nowy STOP. Trening zamknął się normalnie
12:08:20 UTC, returncode0, guard forced[]. Wszystkie procesy należące do próby zamknięte;
W&B `1rd6oj0m` finished (API). Zachowano cp25112,
SHA `37188c52fc549c26f4c31b792678a10fa3308b1cd32666c76dd7d0342999577f`.
112021/145408 transitions, 25112 updates, credit393.25,
earned=accounted25505.25, finite i fingerprint match. Budżet NIE ukończony,
credit NIE drained. Ewaluacja jazdy NIE rozpoczęta, brak wyniku 0/10 lub PASS dla tej próby.
Full SD nadal BLOCKED; QR29/30, mediana54.3s pozostaje zachowanym wynikiem.

Dowody: BASE/queue-sd-sac-actorlr0009-20261006/human-stop-receipt.json oraz
BASE/sd-sac-stopped-analysis-20261006/saved-checkpoint-inspection.json.
Odczyt istniejącego checkpointu na CPU: zero optimizer steps, zero learner updates,
bez środowiska/kontrolera/nowych eksperymentów. Zamrożone runtime bez zmian.
Poniższe wpisy ACTIVE i zgody na następne piloty są historyczne.

## Świeży pilot actor LR9e-4 uruchomiony — 6 października 12:20 Warsaw

`queue-sd-sac-actorlr0009-20261006`, fresh `tmrl-repair-sd-sac-actorlr0009-s17`.
Start 10:20:15.518330 UTC, SAVE14:10:15.518330 UTC (16:10Warsaw),
HARD14:20:15.518330 UTC (16:20Warsaw), cap14400s bez przedłużenia.
145408 transitions/max11400s, potem 10 greedy/max2100s.
Nowy frozen runtime `C:/Users/szulc/.codex/worktrees/tmrl-sd-sac-actorlr-runtime/AITrackmania`
commit `c72591eda6415bd36ee18e5c4fe8eceddacd4e9c`, nie edytować podczas próby.
Zmiana względem best target.8/beta.0005 wyłącznie actor_learning_rate9e-4;
krytyk i temperatura3e-4, nagroda/model/replay/UTD bez zmian. Domyślny parametr
zachowuje dotychczasowe zachowanie; starych checkpointów nie wznawiano.

33 testy algorytmu, 24 guard/candidate/closure tests, Ruff i validate-only passed.
Actual preflight240ms/33 fields/UID ready. Runner66756 created1791282014.9514704,
launcher65000, guard69604, trainlauncher66748, learner45364, actor64172 registered.
W&B `1rd6oj0m` running potwierdzony API; wcześniejsze `awhtibso`/`la0tyfwk` finished.
Przypięto poprzednią normalną closure, dokładne receipts treningu/oceny i audytu;
QR pins i stare STOP hash/mtime zachowane, nowe STOP zawsze wygrywa.
Full SD BLOCKED do rzeczywistej bramki >=8/10 i wszystkich warunków technicznych.
Nadzór ACTIVE, brak automatycznego pełnego treningu.

## Target 1.2: rzeczywista bramka FAIL; następna hipoteza aktora — 6 października 12:16 Warsaw

Ocena fresh02 zakończyła się normalnie 10:11:54.813 UTC, guard closure forced=[];
wszystkie jej procesy zamknięte. 0/10 finishes, średni postęp 0.673439%, no_progress.
1457/1457 pomiarów valid, max/p99 60ms, bez błędów kontrolera/telemetrii,
skips3120/max6; checkpoint SHA niezmieniony. Wszystkie warunki techniczne bramki
spełnione, jazda FAIL. Wynik target1.2 gorszy niż target.8 beta.0005 (48.4221%).

Audyt CPU exact frozen4706, 1024 replay states, threads2/CUDA-1, bez kontrolera
ani aktualizacji learnera: na starcie aktor wybiera akcję5 (pełny skręt z brake tap)
z prawdopodobieństwem około .969, krytyk akcję41 (prosto z brake tap).
1000 kroków niezależnej kopii głowy przy stałym Q podniosło zgodność aktor/Q
z .340 do .804/.807 dla beta0/.0005. Usunięcie kotwicy daje podobny wynik;
próba nie zapisuje polityki i nie dowodzi poprawności krytyka ani jakości jazdy.

Następna hipoteza: wrócić do lepszego target.8/beta.0005 i przetestować wyłącznie
szybsze dopasowanie aktora (actor LR9e-4 zamiast3e-4). Krytyk i temperatura
zachowają LR3e-4. Dodano opcjonalny parametr SD-SAC z domyślnym zachowaniem
bez zmian; nowa próba wymaga świeżego treningu i osobnego zamrożonego źródła.
Dowody: `artifacts/tmrl-test-comparison/sd-sac-target120-audit-20261006`.
Full SD BLOCKED; QR PASS zachowany. Poniższy ACTIVE fresh02 jest historyczny.

## Target 1.2: nowa ocena zachowanego checkpointu uruchomiona — 6 października 12:09 Warsaw

Po ręcznym przywróceniu wtyczki potwierdzono protokół 2 i właściwy UID.
Świeża, osobna kolejka `queue-sd-sac-target120-eval-fresh02-20261006` ocenia
checkpoint 33859 SHA `a7e7aadb5d6860263c4f7c37b5bfe3f5ab19d6d8aa1d31e95242efa07dced16c`.
Tylko 10 przejazdów/max2100s, bez learnera i bez ponownego treningu.
Stary trening pozostaje zakończony, wygasłe recovery01 pozostaje nieuruchomione;
przypięto jego dowody i pierwotne zamknięcie. Nie przedłużono jego limitu.

Nowy plan ma osobny cap do 3000s: start 10:09:44.076605 UTC,
SAVE 10:49:06.272848 UTC, HARD 10:59:06.272848 UTC.
8 testów i validate-only passed; pierwszy testowy błąd dotyczył ścieżki tymczasowej
pytest, poprawiono wyłącznie miejsce plików testowych poza frozen runtime.
Rzeczywisty preflight 300ms/33 fields/UID ready. Runner 67284, guard 35756,
evaluation launcher 68372; W&B `awhtibso` online. Full SD BLOCKED do wyniku bramki.
QR PASS zachowany, źródła frozen4706 bez zmian, brak automatycznego full training.
Poniższe stany oczekiwania na ręczne przywrócenie wtyczki są historyczne.

## Target 1.2: limit recovery minął bez uruchomienia oceny — 6 października 11:58 Warsaw

Pierwotny HARD 09:48:43.413685 UTC minął. Przygotowana kolejka
`queue-sd-sac-target120-eval-recovery01-20261006` nie została uruchomiona:
brak launch receipt, learnera, kontrolera i oceny. Kontrola po HARD nie wykazała
procesów Python ani nasłuchu telemetrycznego 9000/9001. Nie przedłużono limitu.
To **brak wyniku jazdy**, nie 0/10; checkpoint 33859 i kompletne dowody treningu zachowane.

Pulpit i gra zostały wcześniej przywrócone, oryginalna mapa załadowana w walidacji.
Aktualną blokadą jest odrzucenie TrackmaniaRL_Connect przez Openplanet:
`Plugin is not suitable for the current signature mode. It requires School mode.`
Poproszono o ręczne przywrócenie School mode i załadowanie wtyczki; ustawienia
bezpieczeństwa nie są zmieniane automatycznie. Po tej interwencji potrzebny jest
nowy, uzasadniony i ograniczony plan; wygasłego recovery nie uruchamiać.
Full SD nadal BLOCKED, QR PASS zachowany, nadzór ACTIVE. Dowód:
`artifacts/tmrl-test-comparison/queue-sd-sac-target120-eval-recovery01-20261006/deadline-expiry-receipt.json`.
Poniższe wcześniejsze stany i możliwość uruchomienia recovery przed HARD są historyczne.

## Target 1.2: trening kompletny, ocena jeszcze nie rozpoczęta — 6 października 11:10 Warsaw

Nadrzędny stan: trening `tmrl-repair-sd-sac-target120-s17` zakończył się o 08:50:54 UTC.
145437/145408 transitions, 33859 updates, credit .25, earned=accounted 33859.25;
checkpoint finite/fingerprint/accounted/drained/budget_complete. SHA
`a7e7aadb5d6860263c4f7c37b5bfe3f5ab19d6d8aa1d31e95242efa07dced16c`.
Ocena nie ruszyła: preflight o 08:51:09 UTC odrzucił reset, który nie wrócił do startu.
To **brak wyniku jazdy**, nie 0/10. Normalna closure o 08:51:09.665 UTC, forced_owned_pids=[];
runner/guard/learner/actor zamknięte. Dowody starej kolejki pozostają zachowane.

Przygotowano osobną ocenę tego samego checkpointu:
`artifacts/tmrl-test-comparison/queue-sd-sac-target120-eval-recovery01-20261006`.
Validate-only i 8 testów zabezpieczeń passed; tylko 10 ocen/max2100s, bez learnera.
Przypięto poprzednie receipts/source/checkpoint/QR oraz STOP i pierwotne deadlines:
SAVE 09:38:43.413685 UTC, HARD 09:48:43.413685 UTC. Bez przedłużenia cap.
Recovery **nie uruchomiono**. Gra została zamknięta; ponowne uruchomienie nie utworzyło procesu.
Windows zwrócił `GetCursorPos: access denied 0x80070005`; poproszono użytkownika
odblokowanie pulpitu/zamknięcie ewentualnego okna systemowego. Przyczyna resetu nieudowodniona.
Full SD nadal BLOCKED; QR 29/30 median54.3 PASS zachowany. Monitor ACTIVE.
Poniższe wcześniejsze stany ACTIVE target120 są historyczne.

## SD-SAC beta .0005 nie zdał; świeży target 1.2 — 6 października 07:48 Warsaw

Poprzedni `queue-sd-sac-anchor0005-20261006` zakończył się normalnie o 05:36:38 UTC.
Wszystkie jego owned procesy zamknięto bez force-kill. Trening osiągnął 145429/145408 transitions,
33857 updates, credit .25, earned=accounted 33857.25; kompletny/drained/accounted/finite/fingerprint checkpoint.
SHA `f3b701086fa43071edcdf212ff7c6d4259a7c0fe8f494556e834c6c3caa383a3`.
Dziesięć ocen greedy: **0/10 met**, mean progress48.4221%; siedem prób około41%, trzy około65%.
12140/12140 timing valid, max60/p9950ms, no controller/telemetry errors, skips23928/max6.
W&B train6r1s96ly/evalg3248vg6 finished. Wszystkie techniczne warunki bramki spełnione; jazda FAIL.
Full SD pozostaje **BLOCKED**. Nie wznowiono checkpointu ani starej kolejki.

CPU audit dokładnego checkpointu w frozen4706/root PYTHONPATH/threads2/CUDA hidden, zero learner updates/no controller:
anchor gradient .001220 vs value .011101, cosine +.5765; projected cancellation -.0633.
Poprzednia hipoteza konfliktu anchor nie opisuje już tego checkpointu. Entropymean .720/maxprob .790,
actor/Q greedy agreement .302; te wartości nie dowodzą poprawności krytyka ani jakości jazdy.
Niezależne actor-head copies, frozen Q/encoder,1000 kroków,beta.0005: alpha.004555 vs.01 daje
entropy.8997 vs1.2926/maxprob.6752 vs.5841 przy expectedQ cost .00343. Bez zapisu polityki/checkpointu/jazdy.
Wyższy target1.2 ma sprawdzić hipotezę przedwczesnego skupienia polityki i niedostatecznej eksploracji.
Pierwszy audit z niewłaściwym PYTHONPATH nie przeszedł walidacji spec przed update; zachowano log.
Powtórzenie z exact frozen root/fingerprint/SHA przeszło. Nie użyto wyników z main jako dowodu.

NOWY `queue-sd-sac-target120-20261006`, fresh `tmrl-repair-sd-sac-target120-s17`, frozen4706a06b bez zmian.
Jedyna zmiana learning: target entropy .8→1.2; beta.0005/reward/model/GNN/LR/replay/update ratio unchanged.
145408/max11400s +10greedy/max2100s, całkowity cap14400s od tego świeżego startu; bez przedłużenia poprzednika.
Start05:48:43.413685UTC=07:48Warsaw, SAVE09:38:43.413685UTC=11:38Warsaw,
HARD09:48:43.413685UTC=11:48Warsaw. Launcher47728/runner62204created1791265722.9196036,
guard55592,trainlauncher67920/learner29452/actor66932,W&Bla0tyfwk. Preflight280ms/33fields/właściwy UID ready.
Learner ready, actor registered/collecting; to nie wynik bramki jazdy.
28 guard/strict candidate/previous receipt closure tests passed, validate-only passed. Początkowy błąd temp-root
oraz stary regex komunikatu w skopiowanym teście poprawiono w nowym external helper/test; final28passed.
Zachowano pinned poprzednie receipts/normal closure/QR reservation i plan; QR29/30median54.3PASS nie powtarzaj.
Nowy STOP wygrywa; stare pinned STOP hash/mtime unchanged. Nie ma drugiego kontrolera.

Bramka niezmieniona: >=8/10met oraz complete/drained/accounted/finite/fingerprint/SHA,
10complete validUID/alltimingmax100ms/noerrors/skips. Full/manual readiness nadalBLOCKED.
Nadzór15minACTIVE; podSAVE pozostanie wturnwaitmax60s do closure/HARD, bez procesów learner/controller poHARD.
Autonomiczna uzasadniona diagnoza poFAIL, bez full/miesięcznych autostartów/sharedreward/override/replayreset.
Dowody: artifacts/tmrl-test-comparison/sd-sac-anchor0005-audit-20261006/ oraz obie zachowane kolejki.
Poniższe starsze stany/deadlines są historyczne.

# Decyzja przed pełnymi treningami

## SD-SAC beta .005 nie zdał; świeży beta .0005 — 6 października 04:18 Warsaw

SD recovery01 zakończył się normalnie o 04:09:53 Warsaw; guard zamknął wszystkie owned procesy bez force-kill.
Trening osiągnął 142346/145408 transitions, 32540 updates; credit 546.5, earned=accounted 33086.5.
Checkpoint finite/fingerprint, SHA `0efa7b27cc6aacc5bf67696d2d85ab7a78b4230bab74d896d6b2c5a845259498`.
Budżet niekompletny/niedrained: niekwalifikowany. Dziesięć greedy ocen: **0/10 met**, średni postęp 22.0199%;
6684/6684 timing valid, max/p99 50ms, brak controller/telemetry errors, skips 7930/max6.
To częściowy postęp względem beta .5 (3.5517%), bez dowodu użytecznej jazdy. Full SD pozostaje **BLOCKED**.

CPU audit dokładnego checkpointu w frozen 4706, threads2/CUDA hidden, zero learner updates/no controller:
na 1024 replay stanach anchor gradient .023843 vs value .021992, cosine -.7243, projection cancelled .7849.
Q clipping blokował ~.1–.2% stanów. Lokalny konflikt utrzymuje się, ale audyt nie dowodzi poprawności krytyka.
Niezależne kopie samego actor head/frozen Q po 1000 krokach: beta .005 entropy1.9345/maxprob.4442,
beta .0005 entropy.8965/maxprob.6935, expected Q +.0088. Bez zapisu polityki/checkpointu lub jazdy;
ta hipoteza wymaga rzeczywistego pilota i ocen.

Na podstawie bezpośredniej autoryzacji dalszych autonomicznych napraw uruchomiono NOWY świeży test
`queue-sd-sac-anchor0005-20261006`, run `tmrl-repair-sd-sac-anchor0005-s17`, frozen 4706a06b bez zmian.
Jedyna zmiana learning: beta .005→.0005; target .8, reward/model/GNN/LR/replay/update ratio bez zmian.
145408 transitions; osobny limit train11400s zamiast10800s uzasadnia zaobserwowane ucięcie poprzednika;
10greedy/max2100s; CAŁY cap14400s, SAVE600s przed HARD. Starego pilota nie przedłużono ani nie wznowiono.
Start02:18:21.154620UTC=04:18Warsaw, SAVE06:08:21.154620UTC=08:08Warsaw,
HARD06:18:21.154620UTC=08:18Warsaw. Actual preflight250ms/33fields/właściwy UID ready.
Runner58428/launcher54820, guard52900, trainlauncher67476, learner67128/actor63900.
26 testów guard/strict candidate limits/previous closure passed; validate-only passed.
QR nadal PASS29/30/median54.3; pinned QR reservation/plan i receipts pozostają niezmienione.
Nowy STOP wygrywa; stare superseded STOP mają te same przypięte hash/mtime. Żadnego drugiego kontrolera.

Bramka SD niezmieniona: pełny/drained/accounted/finite/fingerprint/SHA checkpoint, 10 ważnych ocen,
>=8/10 met, timing wszystkich max100ms, brak errors i raport skips. Do tego czasu full/manual readiness BLOCKED.
Nadzór ACTIVE15min; dalsza uzasadniona naprawa po FAIL, bez automatycznych miesięcznych startów.
Dowody: artifacts/tmrl-test-comparison/sd-sac-iterative-repair-20261006/{checkpoint-audit.json,actor-anchor-probe.json,next-hypothesis-decision.json}
oraz oba zachowane queue receipts. Poniższe starsze stany są historyczne.


## QR bramka zaliczona, SD-SAC recovery — 6 października 01:03 Warsaw

QR retry02 ukończył 145448 przejść /33862 aktualizacje, earned=accounted=33862,
credit0, finite, fingerprint i potwierdzony SHA
6530a914dfe24037ce967241b4eaa72ea2b8609d6be467a87744376e317af5ab.
Kompletne 30 greedy: 29/30 met, median54.30 s, mean54.233103 s, best52.95 s,
32288/32288 ważnych pomiarów, max60/p9950 ms, bez błędów controller/telemetry,
skips46685/max6. qr-comparison-decision.json: gate_passed=true wobec baseline
26/30 i median56.915 s. To wynik jednego seeda/polityki; nie dowodzi globalnej
optymalności ani ukończenia miesięcznego treningu lub kwalifikacji trzech seedów.
Normalne zamknięcie kolejki 22:50:35 UTC, guard closed normally/forced[].

Pierwsze przejęcie SD-SAC retry02 nie rozpoczęło learnera: confirm_ready odrzucił
player_not_ready. Odczyt okna wykazał końcowy ekran ostatniej walidacji QR.
Po potwierdzeniu ekranu i wybraniu widocznego Improve przywrócono local player
na starcie. Nie zmieniono mapy, nagrody ani frozen sources; stara kolejka,
failure i normalne guard closure zachowane. Read-only/checks i bounded probe
potwierdziły UID oqIJ5rQDRrNwLPTh9H2p_W4tLof, 33 pola i race290 ms.

NOWY recovery queue-sd-sac-anchor005-recovery01-20261006 prowadzi tylko pozostałe
SD-SAC145408/max10800 +10greedy/max2100 na4706a06b, beta.005/target.8.
Fresh run tmrl-repair-sd-sac-anchor005-s17-retry02-recovery01, bez starego cp.
Runner38704, launcher58684, learner43504, actor28068, guard66512.
Start23:03:00 UTC (01:03 Warsaw), rzeczywisty preflight210 ms/33fields/UIDready.
ZACHOWANO pierwotny SAVE2026-10-06T02:40:37.901224UTC (04:40 Warsaw) i
HARD02:50:37.901224UTC (04:50 Warsaw), nie odnowiono czterogodzinnego cap.
Budżet recovery13657.145471 s; helper Budget przyjmuje wcześniejszy deadline,
odrzuca zmianę deadline oraz recovery już uruchomionego learnera/force closure.
24 testy guardów i nowych ograniczeń przeszły; validate-only passed.

SD-SAC nadal BLOCKED: bramka wymaga pełnego/drained/accounted/finite cp,
fingerprint/SHA, 10 kompletnych ocen z prawidłowym UID/timing max100 ms,
bez błędów, raport skips i >=8/10 met. Aktualny start nie jest wynikiem jazdy.
PPO historyczne3/10 nadal ogranicza pełny start. Monitor ACTIVE15min;
po SD FAIL kontynuować uzasadnioną autonomiczną diagnozę świeżym bounded pilotem,
bez automatycznych miesięcznych startów; każdy nowy STOP nadrzędny.


## Autonomiczne wznowienie po pauzie — 5 października 22:12 Warsaw

Użytkownik odwołał pauzę: „Ogarnij wszystko sam, ja idę spać”, następnie
„Nawet jak będzie problem to sam to ogarnij”. Nowe ograniczone próby retry02
zachowują checkpoint zatrzymanego QR retry01 i wszystkie stare STOP jako dowody.
RESUME-AUTHORIZATION przypina ich hash i mtime; każdy nowy lub dotknięty STOP zatrzymuje.
Nie wznowiono starego runnera ani checkpointu na innym kodzie.

Po ponownym uruchomieniu gry przywrócono obraz i istniejącą wtyczkę telemetrii.
Pierwsze otwarcie kopii mapy w edytorze zgłaszało brak startu; bez zapisywania
zmian zamknięto ją i otwarto oryginalny zapis My Maps/tmrl-test.Map.Gbx.
Gra pokazuje VALIDATED i start, session protocol potwierdza oczekiwany UID
oqIJ5rQDRrNwLPTh9H2p_W4tLof oraz ready. Dokładnej przyczyny pierwszego otwarcia
nie udowodniono. Nie zmieniono geometrii, nagrody ani zamrożonych źródeł.

QR queue-qr-repair-retry02-20261005 rozpoczęty 20:12:16 UTC (22:12 Warsaw),
SAVE 23:32:16 UTC (01:32 dnia 6 października), HARD 23:42:16 UTC (01:42).
Cap 12600 s, 145408/max8100 + 30 greedy/max2700, źródła c4ec36a0.
Bramka pozostaje >=29/30, median<=56.915 s, complete/drained/accounted/finite/
fingerprint/SHA i valid timing max100/noerrors/skips. Nie ma jeszcze oceny jazdy.
31 testów nadzoru QR przeszło w tym wznowieniu; plany QR i SD validate-only przeszły.

SD queue-sd-sac-anchor005-retry02-20261005 czeka pasywnie, bez drugiego kontrolera,
na normalne zamknięcie obu etapów nowego QR, kompletny checkpoint/30 ocen z matching
SHA, normalny guard, zamknięte procesy, wolny mutex i brak nowego STOP.
Pasywny limit 23:47:16 UTC (01:47 Warsaw). Potem fresh beta.005/target.8 seed17,
4706a06b, 145408/max10800 +10greedy/max2100, cap14400 s od faktycznego startu,
SAVE600 przed HARD. >=8/10 plus kompletne bramki wymagane; full SD pozostaje BLOCKED.
PPO ostatnio 3/10 i SD beta.5 0/10 nadal są ograniczeniami, nie nowymi sukcesami.

Monitor ACTIVE15min kontynuuje autonomiczne diagnozy i uzasadnione ograniczone
nowe piloty do użytecznej jazdy SD-SAC albo nowego STOP. Żadnych automatycznych
miesięcznych startów, zmian wspólnej nagrody lub obejścia fingerprintu.


## Nowe ograniczone QR → SD-SAC uruchomione — 5 października 17:04 Warsaw

Użytkownik potwierdził: **„Tak, nowe ograniczone QR → SD-SAC”** po pytaniu
o nowy pilot QR do 3,5 godziny i osobny SD-SAC do 4 godzin. To nowa próba,
bez przedłużania lub restartowania kolejek zakończonych awarią.
Poprzednie awarie i wyniki PPO 3/10 oraz SD-SAC 0/10 pozostają zachowane.

Lokalny gracz i telemetria wróciły. Preflight wymaga gotowego gracza przed wejściem,
pomija bezwarunkowe potwierdzenie finish-screen, łączy telemetrię po resecie
i odrzuca brak powrotu na start (race_time > 2500 ms). Osobny test live potwierdził
reset do 210 ms; właściwy QR preflight do **240 ms**, właściwy UID i 33 pola.
Nie udowodniono, który element dawnego menu spowodował utratę gracza.
Zmiany dotyczą wyłącznie zewnętrznych helperów; zamrożone algorytmy są niezmienione.
Pięć testów kontraktu preflight, 31 testów nadzoru QR i 20 SD-SAC przeszło;
oba plany przeszły validate-only.

QR działa w `queue-qr-repair-retry01-20261005`: launcher 43888 / runner 51928,
train launcher 58120, learner 53772, actor 53428; W&B **5x4ydddg online**.
Fresh run `tmrl-repair-qr-loss-sum-s17-retry01` zbiera rollouts, bez gotowego wyniku.
Start **17:03:16 Warsaw**, SAVE **20:23:16**, HARD **20:33:16**, cap 12600 s.
Plan zachowuje 145408 kroków / max 8100 s i 30 greedy / max 2700 s,
zamrożony kod `c4ec36a0`. Bramka pozostaje >=29/30 i mediana <=56,915 s,
pełny/drained/accounted checkpoint, finite/fingerprint/SHA, ważny timing max100 ms,
brak błędów i raport pominiętych ramek. Naprawa matematyczna nie gwarantuje jazdy.

Nowy SD-SAC `queue-sd-sac-anchor005-retry01-20261005`: launcher 58956 /
waiter 30764, created_time 1791212631.7032077; czeka **bez kontrolera i launch.json**.
Przypina nowy QR plan/rezerwację, wymaga obu ukończonych etapów, pełnego finite/drained
checkpointu, 30 ocen z matching SHA, normalnego zamknięcia guardu/procesów,
braku STOP i wolnego mutexu. Pasywne oczekiwanie kończy się **20:38:16 Warsaw**.
Po rzeczywistym przejęciu fresh beta0,005 seed17, 145408/max10800 s + 10 greedy/max2100 s,
cap14400 s, SAVE600 s przed HARD. Źródła `4706a06b` są zamrożone i niezmienione.
Wymagane >=8/10 i pozostałe pełne bramki; full SD-SAC nadal BLOCKED.

Aktualne wskaźniki active-queue/pending-queue/sd-sac-pending-queue opisują te nowe próby;
czytaj faktyczne statusy i launch. Nadzór pozostaje ACTIVE co15 min do zakończenia
autoryzowanego celu SD-SAC albo jawnego STOP. Żadnych automatycznych miesięcznych
startów, zmian nagrody, fingerprint override ani wznawiania starych checkpointów.


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


## Aktualizacja — 5 października, wznowienie 10 godzin

Aktualna kampania `queue-overnight-tuning-20261005` działa od **00:50:18**;
zapis do **10:24**, twarde zatrzymanie **10:34 Europe/Warsaw**.
SD-SAC wznowiony z 12 658 kroków i pełnego zapisu. Następnie dwa świeże prefixy
PPO (baseline entropii 0,01 / hipoteza 0,0) i pomiary powtarzalności pozostałych
algorytmów. Plan i warunki wyboru są w [TUNING.md](TUNING.md).
Wcześniejsza kolejka została zatrzymana i nie jest uruchamiana ponownie.
TQC/SAC/QR zachowują pozytywne baseline; IQN wymaga sprawdzenia stabilności,
SD-SAC pozostaje zablokowany, nowe PPO wymaga wyników. Pełnych treningów nie
uruchomiono. Końcowy raport oraz wspólny commit trzech seedów powstaną po testach.

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

## Raport końcowy kampanii — 2026-10-04, 15:41 Europe/Warsaw

**Wszystkie zaplanowane piloty i ich krótkie ewaluacje zakończone.** Nie
uruchomiono pełnych treningów. Aktualna kolejka `queue-status-recovery-20261004`
ma stan `queue_completed`; nie powtarzać etapów ani uruchamiać starych runnerów.
Poniższa tabela i warunki startu zastępują historyczne decyzje dalej w pliku.

| Algorytm / osoba | Trening pilota | Krótka ewaluacja bez eksploracji | Decyzja |
| --- | --- | --- | --- |
| TQC / Kamil | 145 433 kroków; 71/181 met; ostatnie 20/20 | 2/2: 45,24 i 44,06 s; średnia 44,65 s | Pozytywny pilot; baseline bez zmian |
| PPO / Kuba P. | 145 408 kroków; 71 rolloutów, 4280 kroków Adam; 13 met w pełnych śladach | 2/2: 58,27 i 59,13 s; średnia 58,70 s | Działa, wolniejsza jazda; lokalny test timingu |
| IQN / Jakub | 145 418 kroków; 55/200 met; ostatnie 17/20 | 1/2: 49,90 s; nieukończony przejazd 81,27% | Kandydat do dalszych prób; stabilność niepotwierdzona |
| QR / Jakub | 145 425 kroków; 53/174 met; ostatnie 19/20 | 2/2: 57,07 i 56,81 s; średnia 56,94 s | Pozytywny pilot; baseline bez zmian |
| Discrete SAC / Borys | beta 0: 145 412 kroków; 0/246 met, maks. 62,9% | 0/3: postęp 78,92%, 5,44%, 5,40% | **Pełny start zablokowany** |
| Continuous SAC / bez przydziału | 145 416 kroków; 83/198 met; ostatnie 20/20 | 2/2: 43,78 i 44,75 s; średnia 44,265 s | Pozytywny pilot; ręczny pełny start odblokowany |

Continuous SAC ukończył trening o 15:39:08, ewaluację o 15:41:03. Checkpoint
`distributed-update-00033854.pt`: 33 854 aktualizacje, rzeczywisty kredyt 0,0;
wszystkie 2128 sprawdzonych tensorów zmiennoprzecinkowych skończone. Najlepszy
czas treningowy 44,06 s. Wszystkie logowane straty i alpha skończone,
ostatnia logowana alpha 0,02080. W&B treningu `dx93ox8g` i ewaluacji `zpf9xcap`
ma stan `finished`. Oba przejazdy ewaluacyjne mają ważne pomiary odstępów,
max/p99 50 ms i brak błędów telemetrii/kontrolera. Pominięte ramki 94 i 97,
maksimum 3 i 1. W treningu zdarzały się odstępy do 210 ms; ocena lokalnego
timingu nadal jest potrzebna na każdym komputerze.

SAC zachowuje sprawdzone model, nagrodę i hiperparametry. Po tym wyniku
usunięto wyłącznie jego blokadę pełnego startu w `run_assigned.ps1`;
ochrona zajętej gry, istniejącego runu i blokada SD-SAC pozostają aktywne.
To dopuszczenie do dalszego eksperymentu po lokalnym smoke, nie zaliczenie
końcowych progów 30 prób. Dwie próby na jednym seedzie nie dowodzą przewagi
SAC nad TQC ani pozostałymi algorytmami. Nie zmieniono wspólnej nagrody.

Po zmianie launchera przeszły oba testy: SD-SAC nadal blokowany, dopuszczony
SAC zatrzymuje się przy zajętej grze, istniejący run nie otwiera kontrolera.
Ruff i kontrola różnic przeszły. Ponownie sprawdzono 36 schematów i zasoby
map oraz pełne SAC 17/29/43: 2 048 000 kroków, 30 prób, model i learner jak
w pilocie. Wcześniejsze 40 testów oraz 9 syntetycznych CPU update/checkpoint
pozostają walidacją niezmienionego kodu uczenia; nie są testem długiej jazdy.

### Sprawdzenie poprawionego resetu w grze

Po zakończeniu kolejki, przy braku procesów treningu/ewaluacji i STOP,
wykonano bezpośrednie `environment.reset` z nowego checkoutu `tmrl-training-fixes`
na kodzie `03a0f4a2`, bez launcherowego preflightu i bez learnera.
UID `oqIJ5rQDRrNwLPTh9H2p_W4tLof` zgodny; sukces po 12,922 s,
zegar wyścigu 10 ms, 33 pola, `telemetry_health=ok`. Kontroler i klient
telemetrii zamknięte w `finally`. Jest to lokalny test startu/resetu, nie
długi test jazdy ani kwalifikacja sprzętu kolegów. Dowód:
`artifacts/tmrl-test-comparison/queue-status-recovery-20261004/source-live-reset.json`.

### Warunki ręcznych pełnych startów

- Jeden wspólny nowy commit zespołu z obu branchy, osobne checkouty i start
  od zera. Zapisać hash. Nie wznawiać starych checkpointów na nowym kodzie
  ani omijać fingerprintów; zachowany checkout pilotów pozostaje zamrożony.
- Seedy 17/29/43, po 2 048 000 kroków; końcowo 30 greedy trials na seed.
  Konfiguracje pełne i schematy są sprawdzone; nie przenosić wag/replayu pilota.
- Każdy komputer: własna kalibracja sterowania, lokalny smoke nowego kodu,
  sprawdzenie CUDA, UID, W&B, odstępów decyzji i pominiętych ramek.
  Dla PPO szczególnie sprawdzić timing: jeden przejazd miał max 140 ms.
- SD-SAC: najpierw osobny pilot hipotezy celu entropii 2,0 / beta 0 i ewaluacja;
  ta hipoteza jest nadal **nieuruchomiona**, nie jest wybranym pełnym ustawieniem.
  Nie przypisywać niepowodzenia wspólnej nagrodzie ani pewnemu błędowi krytyka.

Dowody końca SAC: `queue-status-recovery-20261004/sac-result.json` i
`tmrl-test-v2-sac-s17-benchmark-20261004T133913799286/evaluation.json` w
`artifacts/tmrl-test-comparison`. Naprawiona awaria statusu Windows zachowała
logi/checkpointy; nowy runner zakończył pozostałe etapy bez błędów. Wszystkie
sprawdzone końcowe checkpointy mają skończone tensory. Instrukcje startu:
[HANDOFF.md](HANDOFF.md); audyt SD-SAC/PPO: [ALGORITHM_AUDIT.md](ALGORITHM_AUDIT.md).

## Historia kampanii — poniższe stany nie są aktualną kolejką

## Wynik QR i start SAC — 2026-10-04, około 13:30

**QR: pozytywny pilot techniczny; pozostawić hiperparametry baseline.**
145 425 kroków, 33 856 aktualizacji, kredyt 0,25; checkpoint
`distributed-update-00033856.pt`, wszystkie 1140 sprawdzonych tensorów
zmiennoprzecinkowych skończone. Trening 53/174 met, ostatnie 19/20,
najlepszy czas 60,74 s. Ewaluacja bez eksploracji **2/2: 57,07 s i 56,81 s**,
średnia 56,94 s. Oba pomiary odstępów ważne, maksimum i p99 50 ms,
błędy telemetrii/kontrolera null. Pominięte ramki 170 i 115, maksimum 3 i 2.
W&B `3gboyqdh` i `lc12mynj` mają stan `finished`.

To kandydat do pełnych prób Jakuba po lokalnym teście nowego wspólnego kodu.
Dwa przejazdy nie zastępują 30 prób na seed i nie dowodzą przewagi QR nad
IQN. IQN miał 1/2 met, ukończony przejazd 49,90 s; szybkość i ukończenia
trzeba raportować razem, bez rankingu algorytmów na jednym seedzie.

Continuous SAC wystartował 13:30:47 Europe/Warsaw, W&B `dx93ox8g` online;
po jego pilocie kolejka wykonuje dwa przejazdy ewaluacyjne. SAC pozostaje
zablokowany w pełnym launcherze do oceny wyniku. SD-SAC nadal zablokowany.
Dowody QR: `queue-status-recovery-20261004/qr-result.json` i wskazany tam
`evaluation.json`. To częściowy raport: kampania oraz monitor nadal trwają
z granicą zapisu 16:05 i zakończeniem 16:15. Test poprawionego resetu nowego
kodu w grze czeka na zakończenie SAC i brak procesów sterujących grą.

## Aktualizacja — 2026-10-04, około 11:25

IQN ukończył 145 418 kroków i 33 854 aktualizacje, zachowując kredyt 0,5.
Końcowy `distributed-update-00033854.pt` ma skończone tensory. Trening:
55/200 met, ostatnie 17/20, najlepszy czas 52,79 s. Krótka ewaluacja bez
eksploracji: **1/2 met**, ukończony przejazd 49,90 s; nieukończony 81,27%.
Oba przejazdy bez błędów kontrolera/telemetrii, maksymalny odstęp zegara 50 ms.
Pominięte ramki nadal występują: 368 i 401, maksimum 2 i 4. Jeden ukończony
przejazd nie potwierdza stabilności i nie zastępuje 30 prób na seed ani nie
pozwala ogłaszać przewagi algorytmu. W&B treningu `queim8uy` i ewaluacji
`m12bec84` potwierdzają `finished`.

QR wystartował o 11:20 Europe/Warsaw, W&B `3gboyqdh` online; po nim SAC.
Windows zablokował podmianę `status.json` starego runnera. Trening IQN
zakończył się niezależnie i zapisano checkpoint; nie powtarzamy go. Nowa
jawna kolejka `queue-status-recovery-20261004` zawiera tylko ewaluację IQN
(już ukończona), QR/eval oraz SAC/eval. Runner ponawia atomowy zapis przy
blokadzie pliku, a przy awarii zatrzymuje i zapisuje dziecko przed wyjściem.
Cztery testy obejmują rzeczywistą blokadę Windows, błąd zapisu, STOP i zajętą
grę. Poprawka jest w zewnętrznym helperze; źródła pilota pozostają zamrożone.
Dowody: `iqn-completion.json`, `iqn-evaluation.json`, `test_runner.py` w kolejce.
Granica zapisu 16:05, koniec kampanii 16:15; pełnych treningów nie uruchamiamy.
To nadal częściowy raport. SD-SAC pozostaje zablokowany; lokalny test nowego
resetu czeka na zakończenie wszystkich procesów sterujących grą.

## Poprawki przed pełnymi startami — 2026-10-04

Przygotowano poprawki w osobnym checkoutcie `tmrl-training-fixes`:

- Timeout pierwszego odczytu telemetrii środowiska przechodzi przez istniejące
  odzyskiwanie: zamknięcie połączenia i restart mapy, zamiast kończyć trening.
  Zachowano kontrolę spadku zegara po restarcie. Launcher dodatkowo uruchamia
  walidację przed pierwszym odczytem, aby uniknąć oczekiwania na timeout.
- PPO loguje `train/rollout` oraz `rollout/finished_episodes` w W&B: wszystkie
  mety z segmentu, rzeczywiste końce epizodów i sztuczne granice osobno.
  Oś W&B korzysta z łącznej liczby kroków, a nie długości pojedynczego segmentu.
  Historyczne piloty zachowują swoje stare logi; ich mety rekonstruuje audyt.
- Launcher blokuje niegotowe pełne SD-SAC/SAC, drugiego kontrolera i istniejący
  katalog runu. `-Pilot` dla SD-SAC wybiera istniejącą hipotezę 2,0 nats / beta 0,
  a dla pozostałych pojedynczy seed pilota. Pełne runy nie startują automatycznie.

Nagroda i hiperparametry baseline PPO/TQC/IQN/QR/SAC pozostają bez zmian.
SD-SAC nadal nie ma wybranego pełnego ustawienia. Wartość 2,0 wymaga jazdy
i ewaluacji; nie jest przenoszona do konfiguracji trzech pełnych seedów.

Weryfikacja bez sterowania grą: 30 testów resetu, treningu i W&B; 8 testów
workflowów actor-critic; testy launchera i ochrony istniejącego runu; ruff i mypy.
Test launchera sprawdza blokadę obu niegotowych algorytmów oraz zajętej gry.
36 konfiguracji i pliki map przeszły kontrolę schematu; wszystkie 9 algorytmów
z manifestu przeszło syntetyczną aktualizację CPU i zapis/odczyt checkpointu.
Po zakończeniu kolejki nadal obowiązuje lokalny test jazdy nowego kodu przed
pełnym startem, szczególnie pomiar timingu PPO. Nie wykonujemy go równolegle.

Nocne piloty i ich ewaluacje nadal używają zamrożonych źródeł `378f9c6a`.
Ich checkout nie został zaktualizowany. Pełne treningi od zera mają używać
nowego wspólnego commita z brancha zespołu, w osobnym katalogu; wszyscy muszą
zapisać jego hash. Starych checkpointów nie wznawiać na nowym kodzie, ponieważ
poprawki zmieniają fingerprint. Zachowany checkout pilotów służy do ich
dalszej ewaluacji i ewentualnego wznowienia bez obchodzenia tej kontroli.

To częściowa gotowość: TQC i PPO mają pozytywne piloty, SD-SAC jest zablokowany,
IQN ma wynik częściowy 1/2, QR pozytywny pilot 2/2; SAC jeszcze trenuje. Termin kampanii 16:15.

## Aktualizacja — 2026-10-04, około 09:20

PPO ukończył 145 408 kroków i 71 rolloutów / 4280 kroków Adam. Ewaluacja
2/2 met: 58,27 s i 59,13 s; checkpoint oraz W&B sprawdzone. W pełnych
śladach treningowych było 13 met, których skrócone logi nie pokazywały.
To działający pilot, ale wolniejsza polityka gazu/hamulca i pojedynczy odstęp
140 ms wymagają uwagi oraz lokalnego testu przed pełnym startem Kuby P.
Hiperparametry baseline i wspólna nagroda pozostają bez zmian.

SD-SAC pozostaje niegotowy: obecny cel entropii utrzymuje rozproszoną politykę;
próbka końcowego checkpointu daje tylko 29,2% średniej masy na pełny gaz bez
hamowania. Niższy cel 2,0 nadal jest nieuruchomionym testem, nie pełną decyzją.
Szczegóły, dowody i ograniczenia: [ALGORITHM_AUDIT.md](ALGORITHM_AUDIT.md).

Na prośbę użytkownika po IQN/QR dodano continuous SAC; termin całej kampanii
wydłużony do 16:15 Europe/Warsaw (zapis od 16:05). Pozostałe wyniki v2 czekają
na ukończenie. Pełne treningi nadal nie uruchamiają się automatycznie.

## Wynik TQC i wznowienie kolejki — 2026-10-04, około 06:45

**Kamil / TQC: pilot v2 przeszedł; pozostawić hiperparametry.** Trening zakończył
145 433 kroki i 33 858 aktualizacji. W checkpointcie końcowym zachowano kredyt
0,25 (ułamek następnej aktualizacji, nie zaległa pełna aktualizacja); wszystkie
sprawdzone tensory są skończone. W treningu 71/181 ukończeń, ostatnie 20/20,
najlepszy czas 43,84 s. Trening i ewaluacja mają stan `finished` w W&B.

Dwa przejazdy bez eksploracji: **45,24 s i 44,06 s**, średnia 44,65 s,
2/2 ukończeń. Brak błędów telemetryki lub kontrolera, maksymalny odstęp
zegara wyścigu 50 ms. Liczniki pominiętych ramek: 98 i 107, maksimum 3.
To pozytywny pilot techniczny i podstawa do pełnych prób po lokalnym teście
oraz kalibracji Kamila; dwa przejazdy nie zastępują końcowych 30 prób na seed.
Nie wnioskujemy o przewadze nad IQN/QR: inny rodzaj akcji i tylko jeden seed.
Konfiguracje pełne TQC dla seedów 17/29/43 pozostają zgodne z pilotem.

[Trening TQC](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/zhp8bg94),
[ewaluacja TQC](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/y4ug6zb6).

PPO po ewaluacji TQC zatrzymał się przy pierwszym resecie: ekran końca
walidacji nie wysyłał ramek, a reset próbował je odczytać przed restartem.
Nie wykonano aktualizacji ani nie zapisano checkpointu; nie jest to wynik
pilota PPO. Log i nieudaną próbę `4g67pfqd` zachowano. Przywrócono gotową mapę
i rozpoczęto jawną nową próbę `tmrl-test-v2-ppo-retry-s17` (W&B `6mmbtw48`).
Pierwszy rollout 2048 kroków i aktualizacja mają skończone straty oraz KL.

Nowy zewnętrzny runner wykonuje przed każdym procesem kontrolę UID,
restart walidacji i potwierdzenie gotowości **przed pierwszym odczytem ramek**.
Kontroler tego sprawdzenia jest zamykany przed uruchomieniem treningu.
Taką samą ochronę ma launcher `run_assigned.ps1` między pełnymi seedami.
To obejście w launcherze; źródła biblioteki i encodera pozostają zamrożone
na `378f9c6a`. Bezpośrednie `trackmaniarl train` z ekranu wyniku nadal wymaga
wcześniejszego powrotu do aktywnej walidacji. Poprawkę samego resetu należy
kwalifikować osobno; nie zmieniać kodu w działającym checkoutcie.

Pozostała kolejka: PPO → ewaluacja → IQN → ewaluacja → QR → ewaluacja.
Każdy pilot ma limit 2 h 15 min i budżet 145 408; zapis graniczny o 13:50.
SD-SAC pozostaje niegotowy. To nadal częściowy raport całej kampanii.

## Wynik SD-SAC v2 — 2026-10-04, około 04:35

To częściowa aktualizacja gotowości. W momencie tej oceny TQC, PPO,
IQN i QR oczekiwały na zakończenie; nowszy stan jest opisany powyżej.

**Borys / discrete SAC: nie uruchamiać jeszcze pełnych treningów.**
Wariant `tmrl-test-v2-dsac080-beta000-s17` zakończył 145 412 kroków i wszystkie
33 853 należne aktualizacje, z zerowym zaległym kredytem. Checkpoint końcowy
`distributed-update-00033853.pt` zawiera skończone parametry. Trening i ewaluacja
zakończyły się poprawnie i zostały zsynchronizowane z W&B.

W treningu: 0/246 ukończeń, maksymalny postęp 62,9%. W trzech przejazdach
deterministycznych: 0/3 ukończeń, postęp 78,9%, 5,4% i 5,4%. Brak błędów
telemetryki lub kontrolera, odstępy decyzji do 50 ms. Liczniki pominiętych
ramek telemetryki były niezerowe; nie oznacza to braku takich pominięć.
Wynik jest niestabilny i nie kwalifikuje konfiguracji do długich prób.

Wyłączenie kary entropii usuwa wykryte hamowanie wyostrzania polityki:
przy zbliżonych 77,6 tys. kroków entropia wyniosła około 3,55 zamiast 4,14.
Nie dowodzi to poprawy wyniku przy wspólnym budżecie. Przy limicie 100 009
kroków obie próby miały zero ukończeń, a maksymalny treningowy postęp wyniósł
46,3% dla kontroli i 41,1% bez kary. Końcowe ewaluacje używały różnych budżetów
treningowych i małej liczby przejazdów; nie ogłaszać przewagi algorytmu lub wariantu.

Następna hipoteza do sprawdzenia: pozostawić karę wyłączoną i obniżyć cel
entropii do **2,0 nats**, zachowując 78 akcji, nagrodę, model, seed, lr i UTD.
Przygotowano `configs/diagnostic/sd-sac-entropy200-beta000-s17.yaml`.
To osobny pilot od zera na 145 408 kroków, z limitem 2–3 godzin i późniejszą
ewaluacją bez losowania akcji. W tej kolejce nie uruchamia się go automatycznie:
pozostały czas należy do TQC/PPO/IQN/QR. Wartość 2,0 nie jest sprawdzonym
ustawieniem końcowym i nie zastępuje konfiguracji trzech pełnych seedów.

[Trening SD-SAC](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/1sukqoq3),
[krótka ewaluacja](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/rz8xioh9).

## Pierwotna ocena — 2026-10-03

**Aktualizacja:** poniżej zachowano pierwotną ocenę. Poprawki i nocny plan v2 są
w [NIGHT_QUEUE.md](NIGHT_QUEUE.md); stan wdrożenia opisany tam jest nowszy.

Planowany start: 2026-10-04, po spełnieniu warunków poniżej.
To ocena gotowości, nie zatwierdzenie wszystkich algorytmów.

| Osoba | Algorytm | Decyzja |
| --- | --- | --- |
| Jakub | IQN + QR | Zachować hiperparametry; sprawdzić wspólne sterowanie |
| Borys | discrete SAC | Najpierw diagnostyka entropii i wydajności |
| Kamil | TQC | Poczekać na wynik pilota |
| Kuba P. | PPO | Poczekać na wynik pilota |

## Co wynika z pilotów

IQN ukończył 102 409 kroków; QR miał budżet 145 408. Nie traktować
różnicy wyników jako dowodu przewagi QR przy równym budżecie.
Pełne próby: 2 048 000 kroków, seedy 17, 29, 43; 30 przejazdów ewaluacyjnych
na końcowy checkpoint. Oddzielać wyniki treningowe (z eksploracją) od ewaluacji.

Discrete SAC: ukończona druga próba `tmrl-test-pilot-sd-sac-s17-1`,
145 412 kroków, 27 852 aktualizacje, 0/113 ukończonych epizodów,
maksymalny postęp około 40,6%. Pierwszej, przerwanej próby nie doklejać
do tej statystyki. Wznowienie drugiej próby kontynuowało jej stan.

W końcowych logach alpha wynosi około 0,777 (początkowo 0,2).
Kod ustawia domyślny cel entropii na 0,98 * ln(78) = 4,2696 przy maksimum
ln(78) = 4,3567. To silna presja na rozproszony wybór akcji.
Jest to hipoteza wyjaśniająca słabą jazdę, nie potwierdzona diagnoza.
Nie ma bezpośredniego logu entropii polityki; statystyka częstości wykonanych
akcji w odcinku trasy nie jest tym samym pomiarem.

## Hiperparametry

- IQN / QR: pozostawić lr=1e-4, gamma=0,995, batch=256, n_step=1,
  target_update_interval=1000 i epsilon 0,3 -> 0,01 przez 500 000 kroków.
  Oba uczą się kończyć mapę; nie ma jeszcze podstaw do zmiany tych parametrów.
- Discrete SAC: porównać obecny wariant z
  `configs/diagnostic/sd-sac-entropy080-s17.yaml`.
  Jedyna zmiana algorytmiczna: target_entropy=3,4853670613516736
  (=0,8 * ln(78)). Pozostawić lr=3e-4, automatyczną alpha,
  Q-clip i karę entropijną. Kandydat NIE zastępuje konfiguracji pełnych.
  Wartość 0,8 to propozycja do sprawdzenia, nie wynik strojenia ani zalecenie
  autorów publikacji. Porównać przy tym samym sterowaniu, seedzie i budżecie,
  obejrzeć alpha, critic loss, postęp i osobną ewaluację bez eksploracji.
  Sam brak finiszu w krótkim pilocie nie dowodzi błędu implementacji.
- TQC: na razie pozostawić lr=3e-4, tau=0,005 i obecne obcinanie kwantyli.
  Ocenić po pilocie; nie kopiować discrete target_entropy do ciągłej polityki.
- PPO: na razie pozostawić rollout=2048, minibatch=256, epochs=10,
  lr=3e-4, clip=0,2 i target_kl=0,02. Przed dopuszczeniem sprawdzić
  skończone straty, KL, zmianę polityki, stabilność wartości i checkpoint.
  Zmiana normalizacji nagród wymaga osobnego pilota, nie włączamy jej w ciemno.
- Wspólne: nie zmieniać jednocześnie nagrody, gamma, geometrii, akcji
  i architektury. Pilot diagnostyczny oraz koszty strojenia raportować osobno.

Znaczenie celu entropii badano w
[Target Entropy Annealing for Discrete Soft Actor-Critic](https://arxiv.org/abs/2112.02852).
To uzasadnia sprawdzenie tego parametru, nie dowodzi skuteczności wartości 0,8
w Trackmanii.

Kandydat jest poza automatyczną kolejką i manifestem pełnych prób. Po zwolnieniu
gry oraz sprawdzeniu sterowania uruchom go osobno:

```powershell
uv run python -m trackmaniarl train experiments/tmrl_test_comparison/configs/diagnostic/sd-sac-entropy080-s17.yaml --stop-file artifacts/STOP-sd-sac-diagnostic
```

Nie uruchomiono go podczas tego przeglądu; sprawdzono poprawność schematu YAML.

## Rzeczywisty budżet aktualizacji — warunek przed startem

Przy warmup=10 000 i UTD=0,25 dla 145 412 kroków przypada 33 853 aktualizacje.
Discrete SAC wykonał 27 852: o 17,7% mniej. Kod `_credit_updates` ucina
kolejkę kredytu przy `distributed.max_update_credit=512`; opóźniony learner
może bezpowrotnie stracić aktualizacje. Identyczny YAML nie zapewnia więc
identycznego budżetu uczenia na różnych komputerach.

Na każdym komputerze po warmup mierzyć przynajmniej 15–30 minut stabilnej pracy:
updates_per_s, target_updates_per_s, update_credit, odstępy decyzji
i policy_lag_updates. Kredyt nie powinien stale rosnąć ani dochodzić do limitu.
Najpierw sprawdzić obciążenie CPU/GPU i liczbę wątków learnera.
Nie zwiększać tylko limitu kredytu: to odkłada zaległości i zmienia wiek polityki.
Jeżeli sprzęt nie nadąża, potrzebna jest kontrola tempa zbierania danych albo
jawnie ustalony niższy wspólny UTD dla porównywanych metod off-policy,
z ponownym pilotem. Nie zmieniać interwału 50 ms osobno na jednym komputerze.
PPO ma inny mechanizm aktualizacji; raportować jego epoki i rollout osobno.

## PR #52 — co jest istotne dla tej kampanii

[PR #52](https://github.com/TrackmaniaRL/TrackmaniaRL/pull/52) przejrzany pod kątem
obecnych konfiguracji; nie został tutaj scalony ani przetestowany w grze.

| Zmiana | Znaczenie dla obecnego planu |
| --- | --- |
| Pomiar i korekcja krzywej skrętu | Wysokie: ustawienia gry mogą zlewać różne akcje. Zweryfikować na każdym komputerze przed pełnymi próbami. |
| Domyślna skala prędkości 0,001 -> 1 | Konfiguracje już jawnie ustawiają 1, więc nie naprawia tych pilotów. |
| Ograniczanie postępu per krok zamiast łącznie | Obecnie limit_progress_by_kinematics=false; ta poprawka nie uzasadnia zmiany nagrody w kampanii. |
| Domyślny limit prędkości 100 -> 280 m/s | YAML jawnie ustawia 100; sam merge go nie zmieni. Nie podnosić bez pomiaru nasycenia na tej mapie. |
| Głowy wartości i TD w float32 | Ważne dla mixed precision; obecna kampania już używa float32. |
| Import ghostów i geometria | Niepotrzebne do obecnych prób bez demonstracji, na zapisanej geometrii. |

Rekomendacja: przyjąć i sprawdzić część dotyczącą sterowania przed zamrożeniem
wersji kampanii. Nie uzależniać startu od importu ghostów. Sama dostępność
krzywej nie naprawia sterowania: trzeba ustawić grę, zmierzyć odpowiedź
i w razie potrzeby skonfigurować korekcję.

Po udostępnieniu komendy z PR: na załadowanej mapie, bez działającego treningu,
`uv run trackmaniarl track check-steering`.
Ujednolicić Analog Sensitivity i Analog Dead Zone; zweryfikować rozróżnialność
13 poziomów oraz ich rzeczywiste wartości, także po ewentualnej korekcji.
Krzywa jest lokalna dla ustawień komputera; nie kopiować jej bez pomiaru.
Nie wykonywać pomiaru równolegle z aktorem sterującym grą.

Po zmianie sterowania lub runtime wykonać krótką jazdę każdego algorytmu.
Zamrozić wspólny commit, konfiguracje i mapę przed pełnymi seedami.
Nie zmieniać kodu uruchomionych pilotów ani omijać fingerprintu przy wznowieniu.
Stare piloty na innym sterowaniu pozostają diagnostyką, nie równoważnymi
próbami nowego protokołu.

## Harmonogram i wynik

Na 2026-10-03 około 22:52: TQC trwa (około 17 tys. kroków), PPO czeka w kolejce.
To zapis chwili przeglądu, nie monitor aktualnego stanu.

Jedna pełna próba to co najmniej 28,4 h jazdy przy 20 Hz; trzy seedy
to co najmniej 85,3 h na algorytm, plus restarty i uczenie.
Jakub ma dwa algorytmy kolejno na jednej grze: co najmniej 170,7 h.
Nie obiecywać wyników pełnej kampanii na jutro.

Oddzielnie porównywać IQN/QR/discrete SAC (78 akcji) oraz TQC/PPO
(sterowanie ciągłe); różnice nie wynikają wyłącznie z algorytmu.
