# Audyt DSAC/PPO i dodatkowy SAC — 2026-10-04

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
3 godzin testów jazdy priorytetem jest diagnostyczny pilot DSAC; nie należy
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

Eksploracja DSAC jest natywnym próbkowaniem z rozkładu kategorycznego aktora;
ewaluacja używa jego argmax. Logowana przez infrastrukturę wartość epsilon
nie dodaje w tej ścieżce losowych akcji epsilon-greedy i pozostaje nieaktywna.
Nie należy interpretować jej spadku jako zmniejszania eksploracji DSAC.

Następny test: `configs/diagnostic/discrete-sac-entropy200-beta000-s17.yaml`:
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
