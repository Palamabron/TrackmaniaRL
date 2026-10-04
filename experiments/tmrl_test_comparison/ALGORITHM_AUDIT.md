# Audyt DSAC/PPO i dodatkowy SAC — 2026-10-04

Wspólna nagroda pozostaje bez zmian. TQC nauczył się kończyć mapę w tym
samym protokole, a PPO także ją kończy. Audyt dotyczy polityk, temperatury,
akcji i aktualizacji, bez modyfikowania źródeł działającego treningu.

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
krytyka przez clipping. Brak zgodności argmax nie jest sam w sobie błędem:
aktor optymalizuje też entropię, a średnia różnica Q jest niewielka.

Najmocniej uzasadniona hipoteza pozostaje w konfiguracji entropii. Tabela ma
13 akcji pełnego gazu bez hamowania; rozkład ograniczony do nich ma entropię
najwyżej ln(13) = 2,565. Przy entropii pojedynczego stanu równej celowi 3,485
nawet maksymalnie równomierny podział w obu grupach wymaga co najmniej 23,4%
masy poza tą grupą. To ograniczenie matematyczne, nie dowód, że hamowanie
jest zawsze złe; regulator działa na średniej, a poszczególne stany mają
różne entropie. Obserwowane 29,2% masy w grupie pełnego gazu wskazuje jednak,
że obecna polityka nadal często odpuszcza gaz lub hamuje.

Następny test: `configs/diagnostic/discrete-sac-entropy200-beta000-s17.yaml`:
cel 2,0 nats, kara 0,0, wszystkie inne ustawienia, akcje, model i nagroda bez
zmian. Konfiguracja istnieje i jest sprawdzona, ale **nie została uruchomiona**
i nie jest nowym pełnym ustawieniem Borysa. Sam pomiar CPU nie rozstrzyga
przyczyny nieudanej jazdy; potrzebny kontrolowany pilot i ewaluacja.

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

## Continuous SAC dodany do kolejki

Użytkownik zatwierdził rozszerzenie czasu do **16:15 Europe/Warsaw**.
Po IQN i QR nastąpi SAC od zera, seed 17, 145 408 kroków lub 2 h 15 min,
następnie 2 przejazdy bez eksploracji. Model, ciągłe akcje, nagroda, geometria,
UTD 0,25 i batch 256 zgodne z TQC. Portable configs SAC pilot/full17/29/43
pozostają bez zmian; schema, CPU update i checkpoint round-trip przeszły.

Zewnętrzna kolejka `queue-continuous-sac-20261004` ma supervisor oczekujący
na zakończenie bieżącej kolejki i brak kontrolera. Nie startuje równolegle.
Respektuje STOP w obu kolejkach oraz awarię poprzedniej. Przed uruchomieniem
przełączy `active-queue.json`; `PENDING-SAC.json` wskazuje plan oczekujący.
Nowa granica zapisu 16:05, zamknięcie i raport najpóźniej 16:15. Dotychczasowy
runner IQN/QR ma nadal wcześniejszą granicę 13:50; jeśli skróci QR, ocenić
pozostały czas i jawnie kontynuować z checkpointu przed SAC, o ile pozwala termin.

Raporty i skrypty CPU są lokalnie w `artifacts/tmrl-test-comparison/algorithm-audit-20261004`.
Źródła `.py` biblioteki i encodera pozostają zgodne z `378f9c6a`.
Weryfikacja: 26 testów PPO/GAE/aktorów Gaussa przeszło; sprawdzono schema
SAC, CPU update i checkpoint round-trip, pełne seedy 17/29/43 oraz parser
launchera. Audyt nie uruchamiał dodatkowego kontrolera gry.

## Źródła koncepcyjne

Algorytmy różnią się sposobem ponownego wykorzystania danych; nie zrównujemy
liczników aktualizacji bez uwzględnienia rolloutów, minibatchy i epok.
[Spinning Up: algorytmy](https://spinningup.openai.com/en/latest/user/algorithms.html).
Dobór celu entropii w discrete SAC jest przedmiotem osobnych badań;
[Target Entropy Annealing](https://arxiv.org/abs/2112.02852) i
[Revisiting Discrete SAC](https://arxiv.org/abs/2209.10081) nie zastępują
kontrolowanego testu na tej mapie. Powyższe diagnozy pochodzą z lokalnych
metryk, kodu i checkpointów, a nie z przeniesienia wyników tych prac.
