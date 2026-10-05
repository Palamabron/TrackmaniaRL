# Przygotowanie trzech seedów — 4 października 2026

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
