# Decyzja przed pełnymi treningami

## Wynik DSAC v2 — 2026-10-04, około 04:35

To częściowa aktualizacja gotowości. Nocna kolejka nadal wykonuje TQC, PPO,
IQN i QR; ich kwalifikacja v2 nie jest jeszcze zakończona.

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
