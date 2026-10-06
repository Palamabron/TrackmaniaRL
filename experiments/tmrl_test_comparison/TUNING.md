# Przygotowanie trzech seedów — 4 października 2026

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


## Wznowienie nocne — 5 października, 00:50 Europe/Warsaw

Użytkownik odwołał pauzę i zatwierdził **10 godzin łącznie testów i nadzoru**.
Aktualna kolejka to `queue-overnight-tuning-20261005`, wskazana przez
`artifacts/tmrl-test-comparison/active-queue.json`. Start **00:50:18**, zapis
do **10:24**, twardy koniec **10:34 5 października**. Tej granicy nie
wydłużamy. Pełne eksperymenty pozostają do ręcznego uruchomienia.
Limit liczymy od rozpoczęcia pracy o 00:34, włącznie z przygotowaniem i testami
CPU. `effective-deadline.json` oraz osobny watchdog terminu skracają wewnętrzny
limit runnera liczony od uruchomienia kolejki. Watchdog nie otwiera kontrolera.

Przerwana kolejka z 4 października pozostaje zatrzymana; jej STOP i dane
zachowano. Nowa kolejka wznawia SD-SAC z `distributed-update-00000659.pt`:
**12 658 kroków, 659 aktualizacji, kredyt 5,5**, skończone tensory i zgodny
fingerprint potwierdzone. Odtwarza pełny stan, bez resetowania replay.
Nowy segment W&B: [2fslk8zh](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/2fslk8zh).
Audytowy W&B `dwz2e073` miał wyłącznie setup i zero kroków — nie jest pilotem.

Plan: dokończenie SD-SAC celu 2,0 / beta 0 oraz 10 ocen; świeże PPO baseline
entropii 0,01 i osobno 0,0, każde z maksymalnie 2 h 15 min jazdy i 10 ocenami;
następnie po 30 przejazdów starych końcowych IQN, TQC, SAC i QR, jeśli mieszczą
się we wspólnym terminie. Globalny termin ma pierwszeństwo przed sumą etapów.
Pominięte lub niepełne oceny muszą zostać wskazane w raporcie końcowym.

Oba PPO badają **krótki prefix 145 408 kroków z horyzontem LR 2 048 000**,
nie pełny trening. Pozostałe parametry, seed 17, nagroda i model są identyczne.
Zatrzymanie następuje po potwierdzonym zapisie prefixu lub limicie czasu.
Jeśli zamknięcie zapisze częściowy, nieuczony ostatni rollout, narzędzie jawnie
odrzuca go i wybiera zachowany kompletny checkpoint z równymi licznikami
`processed_transitions` i `transitions`. Przed startem obu PPO ustalono ocenę
na **wspólnym zapisie 70 pełnych rolloutów = 143 360 uczonych kroków**.
Zatrzymanie kolekcji pozostaje przy 145 408; konserwatywna ocena wcześniejszego
zapisu chroni przed nadpisaniem ostatniego checkpointu podczas domykania.
Nie zmieniamy liczników ani zawartości zapisu. Receipt rozróżnia kompletność
wspólnego prefixu od pełnego eksperymentu; `full_training_complete` zawsze false.

SD-SAC zachowuje wcześniej ustalony warunek: cały budżet 145 408, rozliczony
kredyt, finite checkpoint, 10 kompletnych prób, minimum 8 met, ważny timing
wszystkich, max kroku ≤100 ms i brak błędów. Bez spełnienia pozostaje zablokowany.
PPO entropii 0 może być wybrane wyłącznie prowizorycznie, gdy oba prefixy są
kompletne przy wspólnym uczonym budżecie, wszystkie pomiary ważne, brak błędów,
max kroku ≤100 ms, co najmniej 8/10 met, liczba met nie niższa od baseline
i mediana czasu co najmniej 5% lepsza. W przeciwnym razie baseline zostaje;
jeżeli oba warianty zawodzą, nie deklarujemy gotowości i nie ukrywamy wyniku.
Jedno ziarno i 10 prób nie dowodzą optymalności ani przewagi na trzech seedach.

Zabezpieczenia nowego runnera: 19 testów CPU, mutex jednej instancji sterowania,
STOP z zapisem, watchdog twardego terminu, atomowy JSON z ponawianiem,
kontrola zamrożonego commita i potwierdzonego checkpointu. Dwa CPU update /
checkpoint roundtrip PPO przeszły na syntetycznych sekwencjach 64; jazda
używa 2048. Dalsze wyniki będą zapisywane w receiptach i raporcie końcowym.

Podczas preflight wykryto i naprawiono w edytowalnym kodzie pomocnicze problemy:
syntetyczny validator PPO dodawał chronione demonstracje poza pojemność replay
2048; teraz używa jednej pełnej sekwencji on-policy. Fingerprint pakietów
namespace deduplikuje korzenie importów, żeby cwd/PYTHONPATH nie zmieniały
tożsamości tych samych plików. To zmiana nowego kodu zespołu: istniejące piloty
pozostają na zamrożonym `8f440075`, stare checkpointy na `d0dfe645`; żadnych
wznowień na nowym kodzie ani obchodzenia fingerprintu. Nagroda bez zmian.
Regresje po poprawkach: **48 testów przeszło**, Ruff i mypy bez błędów.
Dwa testy PowerShell wywołujące launcher pominięto w ponownym przebiegu,
ponieważ prawdziwy nocny runner posiada globalny mutex; ich pierwsza próba
została prawidłowo zablokowana przez działającą kampanię. Guardów nie osłabiano.

Pełne starty od zera: jeden końcowy wspólny commit, seedy **17/29/43**, po
**2 048 000 kroków i 30 greedy prób/seed**, kalibracja i lokalny smoke.
Dobór SD-SAC i PPO oraz końcowa gotowość pozostają otwarte do wyników tej nocy.

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


Użytkownik zatwierdził osobną kampanię po zakończeniu nocnych pilotów:
**maksymalnie 3 godziny łącznie testów w grze**, od rzeczywistego startu nowej
kolejki. Dawna granica 16:15 dotyczyła zakończonej kampanii. Nowe testy nie
uruchamiają automatycznie pełnych treningów. Nagroda, mapa i przestrzenie akcji
pozostają wspólne i niezmienione.

## Decyzje o ustawieniach

Wybieramy ustawienia poparte dotychczasowymi wynikami, bez deklaracji globalnego
optimum. Dwa przejazdy na jednym seedzie nie wystarczą do tuningu wszystkich
algorytmów. Dokładne wartości są zapisane w generatorze oraz YAML-ach.

| Algorytm | Ustawienia do pełnych prób | Status |
| --- | --- | --- |
| IQN | LR 1e-4, gamma .995, batch 256, UTD .25, target co 1000 aktualizacji, kwantyle 64/64/32 | Bez zmian; dodatkowe 10 ocen starego pilota sprawdzi powtarzalność |
| QR | LR 1e-4, gamma .995, batch 256, UTD .25, target co 1000, 64 kwantyle | Zachować pozytywny baseline |
| TQC | LR 3e-4, tau .005, alpha początkowe .2 uczone, cel entropii -3, 2 krytyków × 25 kwantyli, odcięcie po 2 | Zachować pozytywny baseline |
| SAC | LR 3e-4, tau .005, alpha początkowe .2 uczone, cel entropii -3, 2 krytyków | Zachować pozytywny baseline |
| PPO | LR 3e-4 z liniowym spadkiem do końca 2 048 000 kroków, rollout 2048, 10 epok, minibatch 256, GAE .95, entropy .01, clips .2, value .5, grad .5, KL .02 | Naprawiona inicjalizacja adapterów; hiperparametry bez niezweryfikowanych zmian |
| SD-SAC | Pełne ustawienia jeszcze niewybrane; dotychczasowe pliki full nie są zakwalifikowane | Blokada pełnego startu do wyniku nowego pilota |

Off-policy: uniform replay 1 mln, warmup 10 tys., batch 256, n-step 1,
UTD .25 ze ścisłym budżetem aktualizacji. Wszystkie pełne próby od zera,
seedy **17/29/43**, po **2 048 000 kroków**, **30 ocen bez eksploracji na seed**.
Nie przenosimy wag ani replayu pilota. Każdy komputer wymaga kalibracji,
sprawdzenia UID, CUDA, W&B i timingu. PPO zachowuje wyłączoną dodatkową
normalizację obserwacji i nagrody.

## Kontrolowany test SD-SAC

Główna hipoteza: cel entropii **2.0**, kara kotwicząca **beta 0.0**,
seed 17, **145 408 kroków**, limit treningu **8100 sekund**. Model, nagroda,
przestrzeń 78 akcji, LR, alpha, Q-clip i budżet aktualizacji bez zmian względem
poprzedniej próby beta 0. Pomijamy obliczanie nieużywanej kary przy beta 0;
nie zmienia to skończonej funkcji celu. Plik
`configs/diagnostic/sd-sac-entropy200-beta000-s17.yaml` pozostaje hipotezą,
nie automatycznym wyborem pełnych ustawień.

Po treningu planowane jest 10 ocen SD-SAC, następnie 10 ocen IQN i 5 PPO ze
starych końcowych checkpointów, w granicach wspólnego limitu. Częściowe oceny
trzeba oznaczyć; nie uznawać brakujących prób za ukończone. Stare checkpointy
oceniamy na starym zamrożonym kodzie. To test powtarzalności IQN i timingu PPO,
nie test długiego treningu nowej inicjalizacji PPO.

Porównanie SD-SAC obejmuje równy budżet kroków, mety, postęp, ważność timingu,
błędy, finite losses/checkpoint, alpha i entropię oraz kredyt aktualizacji.
Nie wybieramy parametrów na podstawie samego spadku lossu. Nowe ustawienie
można przenieść do trzech pełnych seedów dopiero po ocenie wyniku jazdy;
w razie niepowodzenia blokada pozostaje. Końcowe 30 prób na seed jest osobną
oceną po pełnym treningu, nie zbiorem używanym do wyboru tej hipotezy.

Przed uruchomieniem ustalamy warunek dopuszczenia SD-SAC: cały budżet 145 408
kroków z rozliczonym kredytem i poprawnym checkpointem, komplet 10 ocen,
co najmniej **8/10 met**, ważne pomiary timingu we wszystkich próbach,
brak błędów kontrolera/telemetrii i maksymalny odstęp decyzji **100 ms**.
Pominięte ramki raportujemy, nie ukrywamy. Ten warunek ogranicza ryzyko
zmarnowania trzech pełnych treningów; nie dowodzi optymalności parametrów.
Przy krótszym zapisie lub niepełnej ocenie hipoteza pozostaje niezakwalifikowana.

## Naprawy i wykonanie

- PPO zachowuje celowo zerowe projekcje trzech adapterów enkodera.
  Pozostałe wagi i zużycie RNG nie zmieniają się. Stare wagi po załadowaniu
  dają te same akcje; wpływ nowej inicjalizacji na naukę wymaga osobnego testu.
- STOP trenera obejmuje także okresową i końcową ewaluację PPO. Przerwanie
  zachowuje checkpoint i nie raportuje niepełnej ewaluacji jako sukcesu.
- PPO zamyka środowisko treningowe przed utworzeniem środowiska oceny.
  Po ocenie okresowej tworzy nowe środowisko, zachowując rosnące identyfikatory
  epizodów. Zamknięcie gamepada usuwa callback i zwalnia urządzenie, także
  po błędzie; ponowne zamknięcie jest bezpieczne.
- Ręczny launcher prowadzi każdy seed przez trening i 30 ocen końcowego
  modelu. Weryfikuje ukończenie budżetu, zapis i fingerprint. PPO używa
  istniejącej końcowej oceny. Niespełniony próg osiągów pozostaje widoczny;
  STOP, błąd i niekompletne dane zatrzymują dalsze uruchomienia.
- Nowa kolejka ma osobny katalog `queue-tuning-20261004`, jeden kontroler,
  atomowy zapis statusu z retry oraz globalny termin zapisu i zamknięcia.
  Launcher i kolejka trzymają wspólną blokadę Windows już przed przygotowaniem
  mapy, aby równoczesne uruchomienie nie tworzyło dwóch kontrolerów.
  Dokładny start, termin i zamrożony commit są zapisywane przy uruchomieniu.
- Wszyscy używają jednego nowego commita zespołu z osobnych checkoutów.
  Runtime pilota zostaje zamrożony na czas uczenia i późniejszych ocen.
  Nie omijamy fingerprintów ani nie aktualizujemy kodu używanego przez proces.

Wyniki poprzedniej kampanii: [READINESS.md](READINESS.md). Audyt matematyki,
ograniczenia i źródła: [ALGORITHM_AUDIT.md](ALGORITHM_AUDIT.md).

## Weryfikacja przed zamrożeniem kodu

- 32 testy cyklu trening/ewaluacja i kontrolera, 25 testów launchera oraz
  10 testów algorytmów dyskretnych przeszły. Testy PPO i adapterów opisuje audyt.
- 14 testów zewnętrznej kolejki, w tym rzeczywista blokada pliku Windows,
  współdzielony mutex, zachowanie STOP i koniec czasu dla procesu testowego,
  przeszło bez sterowania grą.
- 36 YAML-i odpowiada generatorowi. Dla sześciu algorytmów konfiguracje
  pełne różnią się między seedami tylko seedem i identyfikatorem.
- Dziewięć standardowych konfiguracji oraz osobna hipoteza SD-SAC przeszły
  syntetyczną aktualizację CPU i zapis/odczyt checkpointu. Ruff, mypy dla
  zmienionych modułów oraz kontrola różnic przeszły.
- Weryfikator końcowego checkpointu sprawdzono także na rzeczywistych starych
  plikach IQN i PPO, na ich oryginalnym kodzie i konfiguracji, z kontrolą
  fingerprintu. Przerwanego przed ostatnią aktualizacją PPO nie uznaje za pełny.

Powyższe testy nie zastępują nowego pilota jazdy ani lokalnego sprawdzenia
sprzętu zespołu. Ograniczenie nowej inicjalizacji PPO pozostaje jawne.
