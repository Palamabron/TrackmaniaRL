## 2026-10-06 — no-movement diagnosis and offline corrective variant

After “no to ogarnij to”, audited the preserved CP33866 in exact frozen e50b0b02,
CPU only, no controller or learner updates. Across128 recorded starts actor argmax
was always action24=[gas0,brake0,steer-1/3], maxprob0.03947, entropy4.16891;
critic preferred56, agreement0%. This explains why this greedy policy can remain
stationary; the old evaluation did not persist issued commands, so actual backend
execution cannot be reconstructed. It was still a valid driving FAIL0/10.

All137 replay terminal states had mean Q12.368 vs reward-2.046, MAE14.414;
terminal fraction0.09418%, clipped loss blocked9.489% of terminal gradients.
Added explicit optional terminal_value_loss_coefficient (default0 preserves SD-SAC)
to anchor selected true-terminal actions directly to known rewards, normalized
within terminal samples, without bootstrap or clipping. Truncations excluded;
importance weights honored; checkpoint options prohibit changing this objective
on resume. It is an experimental critic objective, NOT a proven driving fix.
Added terminal TD error sum/count diagnostics and issued-control histogram,
measurement completeness and gas mean in future evaluation artifacts. Missing
commands are unknown, not zero gas; commands do not prove game acknowledgement.

Offline independent critic copies,200 CPU regression steps, fixed old bootstrap:
coefficient0 terminalMAE13.921/nonterminalTDMAE0.138;
coefficient1 terminalMAE3.009/nonterminalTDMAE1.995. This tradeoff must remain visible.
Head-only300step probe improved terminalMAE14.105 to13.992 only. Training-data
calibration and frozen targets cannot establish ranking, policy quality or driving.
113 CPU tests, Ruff and mypy passed. No saved model, reward, replay or frozen source
was edited; no game test, evaluation or new pilot launched. Evidence in
BASE/sd-sac-stability-no-movement-audit-20261006. FullSD BLOCKED; automation stays
PAUSED. Fresh training/test requires a new direct human instruction.

## 2026-10-06 17:30 Warsaw — evaluation completed; driving gate FAIL

This supersedes the earlier pre-evaluation failure and paused snapshot below.
After the human instruction “no to ogarniaj”, supervision was repaired and the
already authorized ten trials were completed on the preserved checkpoint,
without repeating training. New queue: queue-sd-sac-stability-eval-recovery01-20261006.
Evaluation ended 15:27:46.118406 UTC; guard normal closure 15:27:46.483867 UTC,
forced[]. All recorded PID/creation-time identities closed; shared mutex free.
W&B wwvg5ikp API finished. Original SAVE16:45:15/HARD16:55:15 UTC were retained.

Actual driving gate FAIL: 0/10 finishes; all trials no_progress, progress0.0%.
All ten trials used the correct map UID, 1000/1000 race-clock measurements valid,
maximum/p99 50ms, no controller or telemetry errors. Skips162 total, maximum4.
Complete training145466/145408,33866 updates, earned=accounted33866.5 and
credit0.5, finite/fingerprint-valid/drained checkpoint remains unchanged:
CP33866 SHA1428c80edfc05f5b341040aa39e6d051893b8c32d3b2648a667c048f5a94cb73.
Recovery performed zero learner updates. Frozen e50b0b02 source and helper hashes verified.
Evidence: the new queue's sd-sac-repair-decision.json, post-evaluation-receipt.json,
deadline-closure.json and actual benchmark evaluation.json.

Supervision repair f68cd0e2 adds bounded identity-aware polling of cached process
objects, avoiding wait-handle reopening; descendants now persist PID plus creation
time. Nine module tests and eleven recovery/supervision regression tests passed;
Ruff passed; type checking passed with only missing psutil stubs ignored.
The original AccessDenied OS cause remains unproven; no system process was modified.
The recovery completed under the repaired supervisor, but did not repair driving.

The experimental soft_q_forward_kl stability variant is NOT qualified for full
SD-SAC or three seeds. QR PASS29/30 median54.3s remains preserved.
Automation PAUSED after completion. No new pilot, training or evaluation without
another direct human instruction. Offline diagnosis may inspect why a single
unchanging action produced no progress; its cause is not yet demonstrated.

## Poprawki kodu SD-SAC po nowym poleceniu człowieka — 6 października 2026

## 2026-10-06 17:12 Warsaw — training complete; queue failed before evaluation

This supersedes the earlier active-pilot snapshot. The repaired experimental
SD-SAC stability pilot completed145466/145408 transitions and33866 updates.
Final CP33866 SHA1428c80edfc05f5b341040aa39e6d051893b8c32d3b2648a667c048f5a94cb73
is preserved. Read-only CPU validation in the exact frozen runtime confirmed
fingerprint match, finite learner state, earned=accounted33866.5 and credit0.5,
drained and complete. No learner was instantiated or updated for this validation.

Queue failed2026-10-06T15:12:40.466247UTC with `psutil.AccessDenied(pid59824)`
from `psutil.wait_procs` while checking descendant closure after training exited.
The exact OS-level cause is unproven. Guard normal closure15:12:40.945327UTC,
forced[], all pinned owned processes closed and shared controller mutex free.
Current PID59824 belongs to svchost; the old descendant creation-time identity
was not persisted. PID reuse is plausible but unproven, and that system process
was not modified. W&B ufoxma8r API finished. Original evidence/helpers,
checkpoint and original deadlines are unchanged. This queue is never restarted.

Driving evaluation NEVER STARTED: no evaluation YAML/history/artifact or driving
score. This is neither0/10 nor a gate PASS. Full SD-SAC remains BLOCKED, QR
PASS29/30 median54.3s preserved. No new pilot/training/evaluation was started.
Monitoring is being paused on completion of this report; a further test requires
new direct human authorization. Recommended offline harness repair: bounded
PID-and-creation-time liveness checks instead of waiting on disappeared process
handles; unknown live identities must continue to block controller handoff.

Evidence: `artifacts/tmrl-test-comparison/queue-sd-sac-stability-20261006/`
`failure.json`, `runner-error.log`, `deadline-closure.json`,
`offline-checkpoint-validation.json`, `post-failure-receipt.json`.


## 2026-10-06 14:55 Warsaw — one repaired experimental pilot active

Latest direct instruction: “Jak wszystko naprawisz odpal pilot SD SAC na nowo”.
The earlier human STOP and incomplete checkpoint are preserved; this is a new run
from zero, with no checkpoint or replay resume. Only this pilot and its ten greedy
evaluations are authorized; no automatic following pilot or full training.

Frozen source `e50b0b0216a658737209b99df6c1515e5367e625` at
`C:/Users/szulc/.codex/worktrees/tmrl-sd-sac-stability-runtime/AITrackmania`.
The explicit experimental variant uses soft-Q forward-KL actor fitting, actor
LR0.0003, temperature LR0.0001 and alpha bounds[0.01,0.2]. Target entropy0.8,
beta0.0005, critic LR0.0003, reward/map/model/GNN/replay/UTD remain unchanged.
Multiple stability controls change together; this pilot cannot isolate their
individual effects or establish canonical SD-SAC performance.

Code regressions: 93 CPU checks including the formerly skipped synthetic loops
passed, then the expanded behavior-entropy module (including both canonical and
forward-KL terminal learning and checkpoint round-trip) passed16 checks. Ruff
passed; 30 external guard/candidate/closure checks and validate-only passed.
This is code evidence, not driving qualification.

Actual queue `artifacts/tmrl-test-comparison/queue-sd-sac-stability-20261006`;
run `tmrl-repair-sd-sac-stability-s17`, W&B `ufoxma8r` API running.
START12:55:15.425207UTC=14:55Warsaw, SAVE16:45:15.425207UTC=18:45Warsaw,
HARD16:55:15.425207UTC=18:55Warsaw. Runner61800(created1791291314.4029312),
guard38544; learner66424 ready, actor51072 registered and collecting.
Real preflight270ms/33fields/protocol2/correctUID.

Train145408/max11400 followed by10greedy/max2100 within14400 seconds;
never extend or restart. The gate still requires >=8/10 finishes plus complete,
finite/fingerprint/SHA-valid, drained/accounted training and ten complete trials
with correctUID, all timing maxima<=100ms, no errors and skip accounting.
No driving result exists yet; full SD-SAC remains BLOCKED. QR PASS29/30,
median54.3s remains preserved. Evidence includes plan/source-freeze,
AUTHORIZATION/RESUME-AUTHORIZATION and actual-launch-receipt.json.


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

# Nocne piloty v2 — 3/4 października 2026

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


## Aktualna noc 4/5 października — jawne wznowienie

Nowy wskaźnik `active-queue.json`: `queue-overnight-tuning-20261005`.
Runner 37100, launcher 37184, start 00:50:18 Warsaw; zapis 10:24,
twardy koniec 10:34 5 października, 10 godzin od początku pracy o 00:34,
łącznie z przygotowaniem. `effective-deadline.json` i watchdog skracają
wewnętrzny limit runnera; nie prowadzą drugiego kontrolera.
SD-SAC resume → 10 ocen → PPO baseline prefix → 10 ocen → PPO entropy0 prefix
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
[HANDOFF.md](HANDOFF.md) i [READINESS.md](READINESS.md). SD-SAC nadal zablokowany.

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
aktualizacje, kredyt 0,5. Nie powtarzamy go ani SD-SAC/TQC/PPO. Dowody awarii
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
Ukończonych SD-SAC i TQC nie powtarzamy.

## Wynik pierwszego etapu — około 04:35

SD-SAC080 bez kary entropii zakończył 145 412 kroków i 33 853 aktualizacje,
z zerowym zaległym kredytem. W treningu 0/246 ukończeń, maksymalny postęp
62,9%. Ewaluacja końcowego checkpointu: 0/3 ukończeń, postęp 78,9%, 5,4%,
5,4%. Entropia zbliżyła się do celu, lecz konfiguracja nie zapewniła stabilnej
jazdy i **nie jest zakwalifikowana do pełnych treningów**. Szczegóły oraz
następny, nieuruchomiony pilot celu entropii 2,0 są w [READINESS.md](READINESS.md).
TQC wystartował o 04:10 Europe/Warsaw; kolejka dalej wykonuje pierwotne
pozostałe etapy. To wynik częściowy, nie końcowy raport całej kampanii.

## Aktualizacja po audycie SD-SAC — 4 października, około 02:00

Aktualny plan zastępuje kolejność opisaną niżej. Po zgodzie Jakuba zapisano
i zakończono kontrolny SD-SAC080 z karą entropii 0,5. Końcowy checkpoint ma
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
Kontrolny SD-SAC nie jest zakwalifikowany do pełnych treningów.

Nowa kolejność:

1. Ewaluacja kontrolnego SD-SAC080: 2 przejazdy (zakończona).
2. SD-SAC080 od zera, z `entropy_penalty_coefficient: 0.0`, następnie 3 przejazdy.
3. TQC, następnie 2 przejazdy.
4. PPO, następnie 2 przejazdy.
5. IQN, następnie 2 przejazdy.
6. QR, następnie 2 przejazdy.

Nowy SD-SAC zmienia tylko karę entropii, zachowując cel `0.8 * ln(78)`, seed 17,
model i budżet. Próba z celem 0,98 została odroczona. Konfiguracja przenośna:
`configs/diagnostic/sd-sac-entropy080-beta000-s17.yaml`.
Ustawień pełnego SD-SAC nie zmieniono przed uzyskaniem wyników rzeczywistego pilota.

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
