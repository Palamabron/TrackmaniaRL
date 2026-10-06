## 2026-10-06 17:56 Warsaw — fresh terminal-correction pilot ACTIVE

Latest human instruction “to ogarniaj, badz bardziej autonomiczny” authorizes one
fresh bounded pilot and ten greedy trials. This supersedes the previous paused
snapshot; it does not resume any saved checkpoint or authorize following/full runs.
Queue queue-sd-sac-terminal-20261006; run tmrl-repair-sd-sac-terminal-s17;
W&B mygl7lrw API running. START15:56:52.234211UTC, SAVE19:46:52.234211UTC
(21:46Warsaw), HARD19:56:52.234211UTC(21:56Warsaw). Total cap14400s;
train145408/max11400 then10greedy/max2100, never extend or restart.
Frozen runtime C:/Users/szulc/.codex/worktrees/tmrl-sd-sac-terminal-runtime/AITrackmania,
commit7704b7f9cfb6c7cdc5f32ad672136b9f8e01437d; never edit/update it.
Single algorithmic change vs stability: terminal_value_loss_coefficient1.
All prior actor/temperature/reward/model/GNN/replay/UTD settings retained.
This remains an experimental variant; no actual driving result yet; fullSD BLOCKED.
New evaluation persists issued controls/gas completeness, without claiming game acknowledgement.
113CPU tests/Ruff/mypy and33 guard/config/closure tests+validate-only passed.
Actual preflight260ms,33fields,correctUID; no new STOP, old hash/mtime pins unchanged;
previous exact owned identities closed, mutex free before launch. Source/helper,
previous training/evaluation/closure/checkpoint and offline audit receipts pinned.
Runner66408(created1791302211.215128),guard64200,learner54428,actor51704;
full identities and current startup evidence in actual-launch-receipt.json.
No UI or second controller during training/evaluation. QR PASS29/30 median54.3s retained.
After outcome verify checkpoint/source, all owned closures, report honestly and
pause monitoring. No automatic following pilot, changed-code resume or full start.

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

### Wnioski i proponowana kolejność naprawy, bez uruchamiania prób

1. **Najpierw sprawdzić wiarygodność krytyka.** W 128 zachowanych stanach startu
   krytyk najwyżej ocenia akcję37: gaz0, pełny hamulec, prosty kierunek. Aktor wybiera59:
   gaz1, skręt+0.5, brake tap, prawdopodobieństwo0.878. W 1024 stanach replay zgodność
   actor/Q wynosi tylko7.62%, ale doprowadzenie jej do100% nie jest celem jazdy.
   Poprzedni target1.2 również nie dawał dowodu poprawności Q. Dodatnie Q~7 przy starcie
   nie dowodzi błędu samo w sobie, bo soft Q zawiera przyszłą entropię i nagrody za postęp.
   Trzeba zestawić predykcje z rzeczywistymi zapisanymi zwrotami, osobno dla startu,
   hamowania, powolnej jazdy i końców epizodów. Dane obserwacyjne nie rozstrzygają jakości
   niewybranych akcji; nie wolno przedstawiać ich jako testu kontrfaktycznego.

2. **Naprawić zapadanie polityki i ustalić spójną regulację entropii.** Zapisany aktor
   ma entropy mean0.271 przy celu0.8, max_probability mean0.923, alpha0.000935.
   W replay historyczna entropia zachowania wynosi średnio3.026; kara zakotwicza więc
   aktora do dużo starszych, bardziej losowych polityk. Samo zwiększenie actorLR nie
   stanowi naprawy: zatrzymana próba ma tylko3 greedy actions w badanej próbce.
   Przed wyborem kolejnych liczb potrzebna jest analiza przebiegu alpha/H i sił składników
   celu. Proponuję oddzielić szybkość aktualizacji temperatury od krytyka oraz kontrolować
   odchylenie od celu i wiek odniesienia. Ewentualna zmiana sposobu kotwiczenia musi być
   jawnie oznaczona jako wariant algorytmu; usunięcie beta nie jest uzasadnione wcześniejszym
   porównaniem beta0/.0005. Minimum alpha lub nowy target nie są jeszcze zatwierdzoną receptą.

3. **Dopiero po ocenie Q poprawić dopasowanie aktora.** Dla dyskretnych78 akcji można
   wyliczyć dokładny rozkład softmax(Q/alpha) i mierzyć odległość polityki od niego osobno
   na startach i w replay. Zapisana średnia KL wynosi28.01, na startach48.57: to rozjazd
   polityki i celu krytyka, nie dowód dobrej jazdy tego celu. Należy ustalić, czy problemem
   są nasycone logity, dryf krytyka, czy reprezentacja. Wariant z aktualizacjami aktora
   przy zamrożonym celu lub z forward-KL distillation może być późniejszą hipotezą,
   ale zmienia regułę uczenia i nie powinien automatycznie zastąpić kanonicznego SD-SAC.
   Powrót do actorLR3e-4 jest punktem odniesienia, nie obietnicą naprawy.

4. **Uczenie wartości musi mieć mierzalny punkt odniesienia.** Jeśli kalibracja ujawni
   zbyt duże poleganie na samych predykcjach przyszłego Q, rozważyć poprawnie zdefiniowane
   wielokrokowe soft targets oraz lepsze pokrycie danych. Nie kopiować bez sprawdzenia
   zwykłego n-step, który może pomijać pośrednie składniki entropii. Nie zmieniać wspólnej
   nagrody, nie usuwać akcji hamowania tylko dlatego, że model je nadużywa: QR na tej samej
   przestrzeni78 akcji potrafił przejść bramkę. Każdą zmianę izolować, po nowej zgodzie.

Nie wykazano błędu znaku podstawowego SAC/alpha ani głównej blokady przez Q-clip.
W odczytanej próbce clipping przekracza limit dla0.20%/0.29% akcji, blokada gradientu0%.
Kod no_progress/slow_progress kończy epizod jako terminated=True, a replay zeruje bootstrap
przy terminated; nie znaleziono tu podejrzewanego błędu doliczania dalszej jazdy po porażce.
Podstawowe double-average Q, entropy penalty i Q-clip odpowiadają konstrukcji z
[oficjalnej implementacji autorów](https://github.com/coldsummerday/SD-SAC/blob/main/src/libs/discrete_sac.py).
Różnica redukcji Q-clip: lokalnie max per próbka, w kodzie autorów max po mean; to różnica
implementacji, której wpływu na tę porażkę nie wykazano.

Przegląd ujawnił też drobny błąd spójności: state_dict_for_policy resetuje actor optimizer
z learning_rate krytyka zamiast actor_learning_rate. Dotyczy ścieżki checkpointu polityki
ocenionej i przyszłego wznowienia; nie wyjaśnia tej świeżej próby bez ewaluacji/wznowienia.
Nie poprawiano algorytmu i nie uruchamiano testów w odpowiedzi na żądanie analizy.

Wniosek: najpierw kalibracja krytyka i kontrola zapadania entropii, potem dopasowanie aktora.
Dalsze strojenie samego beta/target/LR bez tych rozróżnień nie daje uczciwej gwarancji poprawy.
Zmiana9e-4 nie ma końcowego wyniku jazdy, ponieważ człowiek zatrzymał próbę przed końcem.

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

# Continued SD-SAC repair — 5 October 2026

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
