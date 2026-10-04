# Decyzja przed pełnymi treningami

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
ochrona zajętej gry, istniejącego runu i blokada DSAC pozostają aktywne.
To dopuszczenie do dalszego eksperymentu po lokalnym smoke, nie zaliczenie
końcowych progów 30 prób. Dwie próby na jednym seedzie nie dowodzą przewagi
SAC nad TQC ani pozostałymi algorytmami. Nie zmieniono wspólnej nagrody.

Po zmianie launchera przeszły oba testy: DSAC nadal blokowany, dopuszczony
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
- DSAC: najpierw osobny pilot hipotezy celu entropii 2,0 / beta 0 i ewaluacja;
  ta hipoteza jest nadal **nieuruchomiona**, nie jest wybranym pełnym ustawieniem.
  Nie przypisywać niepowodzenia wspólnej nagrodzie ani pewnemu błędowi krytyka.

Dowody końca SAC: `queue-status-recovery-20261004/sac-result.json` i
`tmrl-test-v2-sac-s17-benchmark-20261004T133913799286/evaluation.json` w
`artifacts/tmrl-test-comparison`. Naprawiona awaria statusu Windows zachowała
logi/checkpointy; nowy runner zakończył pozostałe etapy bez błędów. Wszystkie
sprawdzone końcowe checkpointy mają skończone tensory. Instrukcje startu:
[HANDOFF.md](HANDOFF.md); audyt DSAC/PPO: [ALGORITHM_AUDIT.md](ALGORITHM_AUDIT.md).

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
zablokowany w pełnym launcherze do oceny wyniku. DSAC nadal zablokowany.
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
To nadal częściowy raport. DSAC pozostaje zablokowany; lokalny test nowego
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
- Launcher blokuje niegotowe pełne DSAC/SAC, drugiego kontrolera i istniejący
  katalog runu. `-Pilot` dla DSAC wybiera istniejącą hipotezę 2,0 nats / beta 0,
  a dla pozostałych pojedynczy seed pilota. Pełne runy nie startują automatycznie.

Nagroda i hiperparametry baseline PPO/TQC/IQN/QR/SAC pozostają bez zmian.
DSAC nadal nie ma wybranego pełnego ustawienia. Wartość 2,0 wymaga jazdy
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

To częściowa gotowość: TQC i PPO mają pozytywne piloty, DSAC jest zablokowany,
IQN ma wynik częściowy 1/2, QR pozytywny pilot 2/2; SAC jeszcze trenuje. Termin kampanii 16:15.

## Aktualizacja — 2026-10-04, około 09:20

PPO ukończył 145 408 kroków i 71 rolloutów / 4280 kroków Adam. Ewaluacja
2/2 met: 58,27 s i 59,13 s; checkpoint oraz W&B sprawdzone. W pełnych
śladach treningowych było 13 met, których skrócone logi nie pokazywały.
To działający pilot, ale wolniejsza polityka gazu/hamulca i pojedynczy odstęp
140 ms wymagają uwagi oraz lokalnego testu przed pełnym startem Kuby P.
Hiperparametry baseline i wspólna nagroda pozostają bez zmian.

DSAC pozostaje niegotowy: obecny cel entropii utrzymuje rozproszoną politykę;
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
DSAC pozostaje niegotowy. To nadal częściowy raport całej kampanii.

## Wynik DSAC v2 — 2026-10-04, około 04:35

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
Przygotowano `configs/diagnostic/discrete-sac-entropy200-beta000-s17.yaml`.
To osobny pilot od zera na 145 408 kroków, z limitem 2–3 godzin i późniejszą
ewaluacją bez losowania akcji. W tej kolejce nie uruchamia się go automatycznie:
pozostały czas należy do TQC/PPO/IQN/QR. Wartość 2,0 nie jest sprawdzonym
ustawieniem końcowym i nie zastępuje konfiguracji trzech pełnych seedów.

[Trening DSAC](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/1sukqoq3),
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

Discrete SAC: ukończona druga próba `tmrl-test-pilot-discrete-sac-s17-1`,
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
  `configs/diagnostic/discrete-sac-entropy080-s17.yaml`.
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
uv run python -m trackmaniarl train experiments/tmrl_test_comparison/configs/diagnostic/discrete-sac-entropy080-s17.yaml --stop-file artifacts/STOP-dsac-diagnostic
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
