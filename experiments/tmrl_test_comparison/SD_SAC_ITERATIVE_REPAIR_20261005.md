# Continued SD-SAC repair — 5 October 2026

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


The human explicitly instructed: “No to poprawiaj SD SAC tak długo aż będzie sensowny”. This authorizes further bounded fresh SD-SAC diagnostics, with unchanged shared reward. PPO and the already queued QR-DQN run keep their frozen sources, stages and deadlines. A new SD-SAC controller may start only after their normal closure, with no new STOP and a free shared controller mutex. No full monthly training is started automatically. Completion of PPO or QR alone no longer ends the SD-SAC repair objective.

## Evidence from the failed behavior-entropy pilot

The `266e2629` seed17 pilot stopped at its 8100-second limit: 135406/145408 transitions, 30775 updates, 576.5 remaining credit. Earned and accounted credit match, but the complete-budget and drained-credit gates fail. Its ten greedy trials produced **0/10 finishes**, mean progress **3.5517%**, valid timing 1961/1961 measurements, maximum/p99 50 ms, no controller or telemetry errors, 2440 skipped telemetry frames, maximum 5. Full SD-SAC remains blocked.

The matching finite checkpoint SHA is `6fdab80112a7e27a5bfd65cd98e01eb20297f647b4b7258045ea726e82154175`. An offline CPU audit in its exact frozen runtime verified the fingerprint and inspected 1024 replay states plus all 118 episode starts. It created no controller, resumed no live training, and performed no learner updates.

At the sampled checkpoint, alpha was `1.9704e-5`; mean current entropy was 4.2507 nats and stored behavior entropy 4.2883. Mean maximum action probability was only 0.0329. The Q preference gradient norm was 0.0074725; the beta0.5 behavior anchor gradient norm was 0.0080897. Their cosine was **−0.9295**, and the anchor cancelled **1.0059** of the value gradient along its direction. This is a measured conflict on this batch, not proof that beta0.5 is universally incorrect. Q clipping blocked gradients in only 1/1024 and 0/1024 sampled critic entries.

At all recorded starts the actor selected action75 (full throttle, steer+1), while the double-average critic preferred action63 (full throttle, steer−2/3). Q differences were small; better agreement with these critics alone cannot establish useful driving.

## Next isolated hypothesis

`configs/diagnostic/sd-sac-anchor005-s17.yaml` changes the **policy hyperparameter beta0.5 → beta0.005** only. Target entropy stays 0.8 nats, initial alpha0.2, learning rate3e-4, seed17, categorical78 actions, model, uniform replay, gamma0.995, sampling, update ratio0.25 and the shared reward remain unchanged. Full configurations17/29/43 and the full-run block are unchanged pending live evidence.

An independent actor-head probe on frozen encoders and critics used the same 1024 states and original alpha. After 1000 Adam steps, beta0.5 kept mean entropy4.2439 and mean maximum probability0.0298; beta0.005 gave entropy3.5263 and maximum probability0.1331. This supports testing a weaker anchor. These are counterfactual CPU copies, **not a new trained driving policy**, and they were never saved or passed to evaluation.

The candidate starts from random initialization on a separate frozen checkout. Its short budget remains 145408 interactions. The collection/drain stage allows 10800 seconds to avoid repeating the previous premature time limit; ten greedy trials allow 2100 seconds. The entire candidate has a 14400-second cap from its actual start, SAVE 600 seconds before HARD. Its passive waiter has a separate finite deadline and creates no learner or controller. Existing PPO/QR limits are not extended.

## Actual queued reservation

The source commit `4706a06b0eea5ba3fe0d2c6aa1ad641ed29aca84` was atomically published to both team branches and frozen separately in `C:/Users/szulc/.codex/worktrees/tmrl-sd-sac-anchor-runtime/AITrackmania`. Later documentation commits do not change that runtime.

At 13:32:39 Warsaw, the passive waiter was actually started in `artifacts/tmrl-test-comparison/queue-sd-sac-anchor005-20261005`: launcher PID 48368, waiter PID 57588, create time 1791199959.0079837. It has status `waiting_for_predecessor`, an empty error log, and no active `launch.json`, learner or controller. `sd-sac-pending-queue.json` stores this reservation; always read the actual queue status and launch records for current progress. The active pointer still belongs to PPO, followed by the already reserved QR stage.

The waiter expires at `2026-10-05T18:09:10.642910UTC` (20:09 Warsaw). It may start the candidate only after normal QR completion, complete finite/drained/accounted QR checkpoint and 30 evaluation receipts with matching SHA, closed observed owned processes and guard, no new STOP, and a free shared controller mutex. It pins the existing QR plan and process reservation. A failed or incomplete predecessor does not authorize bypassing that handoff. Candidate SAVE/HARD timestamps begin only at its real live launch, never at the passive reservation.

`test-report.json`, `source-freeze.json`, `AUTHORIZATION.json`, `plan.json`, `wait-start.json` and `latest-monitor.json` preserve the local evidence. The new queue's `monitor.py` is read-only and follows its actual current stage; it creates no environment, learner or tracking run. Its deadline guard owns only its runner and children. The heartbeat stays ACTIVE after PPO/QR while continued SD-SAC diagnosis is required under the direct human instruction.

## Source changes and checks

Actor improvement now evaluates detached critic values under `no_grad`, avoiding a critic graph that was immediately discarded. The scalar actor objective and actor gradients are preserved. New diagnostics report maximum action probability, Q action spread, actor/Q greedy agreement, weighted anchor loss, reference entropy and its gap from current entropy. These describe learning; they do not substitute for the driving gate.

The new scalar-reference regression verifies actor gradients independently and confirms that actor improvement builds no critic graph. A 78-action small-value objective test checks that the weaker anchor still allows the known preferred action to gain probability despite stale uniform replay entropy. The complete learning test directory passed 106 tests. Standard CLI validation of the actual GNN/categorical 78 composition completed a CPU synthetic update and zstd checkpoint roundtrip with no controller or W&B initialization. Ruff and mypy for the changed source passed; all 42 experiment configuration schemas passed. The external queue passed 20 supervision tests, including real Windows file locks, bounded retries, incomplete/mismatched predecessor rejection, valid and invalid driving gates, and an owned CPU child deadline test that preserved an existing human STOP. Plan validation passed without starting a controller.

## Success and continuation

Useful single-seed diagnostic behavior requires the complete budget and drained/reconciled credit, finite matching fingerprint/SHA, ten complete map-valid greedy trials, **at least 8/10 finishes**, every timing measurement valid, maximum step 100 ms, no runtime errors and a skip report. If it fails, preserve the result and continue diagnosis under the human instruction; never relabel a failure as success or restart a used run directory. Each further hypothesis needs fresh sources/config identity, a bounded pilot and actual driving evidence. No single result establishes globally optimal HP, 37-second pace, three-seed qualification or monthly readiness.

Local evidence is under `artifacts/tmrl-test-comparison/sd-sac-iterative-repair-20261005/` (`checkpoint-audit.json`, `actor-anchor-probe.json`); direct authorization is `SD-SAC-ITERATIVE-REPAIR-AUTHORIZATION.json` in the comparison artifact root.
