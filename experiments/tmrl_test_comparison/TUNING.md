# Przygotowanie trzech seedów — 4 października 2026

## Nowa kolejka uruchomiona — 4 października, 17:28

Kod zespołu opublikowany na obu branchach: **8f440075**. Nowy pilot korzysta
z osobnego, czystego i zamrożonego `tmrl-tuning-runtime` na tym commicie.
Stare IQN/PPO będą oceniane na zachowanym `tmrl-algorithm-runs` (`d0dfe645`,
źródła Python `378f9c6a`), bez przenoszenia checkpointów między wersjami.

Kolejka `queue-tuning-20261004` wystartowała **17:27:56 Europe/Warsaw**.
Termin zapisu **20:17:56**, twardy koniec **20:27:56**. To zatwierdzone nowe
3 godziny łącznie, nie przedłużanie poprzedniej kampanii. Wskaźnik
`artifacts/tmrl-test-comparison/active-queue.json` wskazuje tę kolejkę.
DSAC `tmrl-tuning-dsac-entropy200-beta000-s17` działa, W&B
[o3aknhmz](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/o3aknhmz)
potwierdzony online/running. O 17:30 zapisano 1943 kroki w fazie warmup,
ważny timing ostatniego epizodu (p99 50 ms, max 60 ms), brak błędu telemetrii.
To kontrola uruchomienia, nie wynik uczenia ani kwalifikacja DSAC.

Następnie planowane są 10 ocen DSAC, 10 IQN i 5 PPO w pozostałym czasie.
Warunki promocji DSAC oraz sprawdzone ustawienia opisuje [TUNING.md](TUNING.md).
Monitor działa co 5 minut i ma zakończyć pracę po raporcie tej kampanii.
Pełnych treningów nie uruchomiono. Końcowy dobór DSAC pozostaje otwarty do
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
| DSAC | Pełne ustawienia jeszcze niewybrane; dotychczasowe pliki full nie są zakwalifikowane | Blokada pełnego startu do wyniku nowego pilota |

Off-policy: uniform replay 1 mln, warmup 10 tys., batch 256, n-step 1,
UTD .25 ze ścisłym budżetem aktualizacji. Wszystkie pełne próby od zera,
seedy **17/29/43**, po **2 048 000 kroków**, **30 ocen bez eksploracji na seed**.
Nie przenosimy wag ani replayu pilota. Każdy komputer wymaga kalibracji,
sprawdzenia UID, CUDA, W&B i timingu. PPO zachowuje wyłączoną dodatkową
normalizację obserwacji i nagrody.

## Kontrolowany test DSAC

Główna hipoteza: cel entropii **2.0**, kara kotwicząca **beta 0.0**,
seed 17, **145 408 kroków**, limit treningu **8100 sekund**. Model, nagroda,
przestrzeń 78 akcji, LR, alpha, Q-clip i budżet aktualizacji bez zmian względem
poprzedniej próby beta 0. Pomijamy obliczanie nieużywanej kary przy beta 0;
nie zmienia to skończonej funkcji celu. Plik
`configs/diagnostic/discrete-sac-entropy200-beta000-s17.yaml` pozostaje hipotezą,
nie automatycznym wyborem pełnych ustawień.

Po treningu planowane jest 10 ocen DSAC, następnie 10 ocen IQN i 5 PPO ze
starych końcowych checkpointów, w granicach wspólnego limitu. Częściowe oceny
trzeba oznaczyć; nie uznawać brakujących prób za ukończone. Stare checkpointy
oceniamy na starym zamrożonym kodzie. To test powtarzalności IQN i timingu PPO,
nie test długiego treningu nowej inicjalizacji PPO.

Porównanie DSAC obejmuje równy budżet kroków, mety, postęp, ważność timingu,
błędy, finite losses/checkpoint, alpha i entropię oraz kredyt aktualizacji.
Nie wybieramy parametrów na podstawie samego spadku lossu. Nowe ustawienie
można przenieść do trzech pełnych seedów dopiero po ocenie wyniku jazdy;
w razie niepowodzenia blokada pozostaje. Końcowe 30 prób na seed jest osobną
oceną po pełnym treningu, nie zbiorem używanym do wyboru tej hipotezy.

Przed uruchomieniem ustalamy warunek dopuszczenia DSAC: cały budżet 145 408
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
- Dziewięć standardowych konfiguracji oraz osobna hipoteza DSAC przeszły
  syntetyczną aktualizację CPU i zapis/odczyt checkpointu. Ruff, mypy dla
  zmienionych modułów oraz kontrola różnic przeszły.
- Weryfikator końcowego checkpointu sprawdzono także na rzeczywistych starych
  plikach IQN i PPO, na ich oryginalnym kodzie i konfiguracji, z kontrolą
  fingerprintu. Przerwanego przed ostatnią aktualizacją PPO nie uznaje za pełny.

Powyższe testy nie zastępują nowego pilota jazdy ani lokalnego sprawdzenia
sprzętu zespołu. Ograniczenie nowej inicjalizacji PPO pozostaje jawne.
