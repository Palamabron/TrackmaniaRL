# Podział eksperymentów

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


## Nowe przygotowanie i testy — 2026-10-04 po 17:00

Po zakończeniu poprzedniej kampanii użytkownik zatwierdził naprawy oraz
**do 3 godzin łącznie nowych testów w grze**. Aktualne decyzje o parametrach,
kolejność prób, poprawki PPO i warunki wyboru DSAC opisuje [TUNING.md](TUNING.md).
Pełne treningi pozostają ręczne; DSAC nadal jest zablokowany do wyniku nowego
pilota. Stare checkpointy zachowują swój zamrożony runtime. Poniższy raport
15:41 i starsze sekcje dokumentują zakończoną poprzednią kampanię, nie nową kolejkę.

## Kampania zakończona — 2026-10-04, 15:41 Europe/Warsaw

Wszystkie zaplanowane piloty i krótkie ewaluacje zakończone. TQC, QR, PPO
oraz continuous SAC mają pozytywne piloty; IQN ukończył 1/2 przejazdów i
wymaga dalszej kontroli stabilności. DSAC pozostaje niegotowy. Pełnych
treningów nie uruchomiono automatycznie. Wyniki, timing i ograniczenia:
[READINESS.md](READINESS.md).

| Osoba | Algorytm | Warunki pełnych treningów |
| --- | --- | --- |
| Jakub | IQN i QR | każdy: 17/29/43, lokalny smoke; IQN stabilność do sprawdzenia |
| Borys | discrete SAC | zablokowane; najpierw pilot 2,0 / beta 0 i wybór ustawień |
| Kamil | TQC | 17/29/43 po lokalnej kalibracji i smoke |
| Kuba P. | PPO | 17/29/43 po lokalnym smoke i kontroli timingu |
| Bez przydziału | continuous SAC | 17/29/43 po lokalnym smoke; ręczny start odblokowany |

Aktualna decyzja przed pełnym startem: [READINESS.md](READINESS.md).
Launcher blokuje pełne DSAC do czasu pozytywnego testu niższej entropii. Dla Borysa przygotowano
wyłącznie test: `run_assigned.ps1 discrete-sac -Pilot` (145 408 kroków, seed 17,
cel entropii 2,0, kara 0,0). Po nim potrzebna osobna ewaluacja bez eksploracji;
skrypt nie przechodzi automatycznie do pełnych seedów.
IQN i QR zakończyły kampanię v2; nie powtarzać ich automatycznie.
Discrete SAC bez kary entropii zakończył pilot, lecz ewaluacja
dała 0/3 ukończeń (postęp 78,9%, 5,4%, 5,4%). **Borys: pełne treningi jeszcze
nie są gotowe do startu.** Przygotowano osobny, nieuruchomiony test celu
entropii 2,0; instrukcję i ograniczenia opisuje READINESS.md.
**Kamil / TQC: pilot v2 zakończony pozytywnie**, 145 433 kroki, 71/181 met
w treningu i 2/2 w krótkiej ewaluacji (45,24 s; 44,06 s). Hiperparametry
pozostają bez zmian; przed pełnym startem wymagany lokalny test i kalibracja.
**Kuba P. / PPO: ukończony pilot**, 145 408 kroków, 13 met w pełnych śladach
treningu i 2/2 w ewaluacji (58,27 s; 59,13 s). Zachowujemy baseline; przed
pełnym startem lokalny test oraz kontrola pojedynczego odstępu 140 ms.
Audyt i ograniczenia: [ALGORITHM_AUDIT.md](ALGORITHM_AUDIT.md).
**Continuous SAC: 145 416 kroków, 83/198 met, ostatnie 20/20**, ewaluacja
2/2 (43,78 s; 44,75 s), max/p99 50 ms, bez błędów. Baseline bez zmian;
nie ma jeszcze przydzielonej osoby. Dwa przejazdy nie zastępują 30 prób/seed.
Końcowy stan kolejki opisuje [NIGHT_QUEUE.md](NIGHT_QUEUE.md).
Pełnych treningów nie
uruchamiamy automatycznie po pilotach. Przed przekazaniem do długich prób
sprawdzamy każdy algorytm: aktualizacje o skończonym lossie, zmiana polityki,
ukończony budżet, poprawny zapis końcowego checkpointu, metryki w W&B,
stabilne sterowanie i brak błędów telemetryki. Pilot nie musi ukończyć mapy,
ale sam działający proces nie jest jeszcze pozytywnym wynikiem testu.

Bezpośredni reset poprawionego nowego kodu sprawdzono lokalnie po zamknięciu
kolejki: zgodny UID, telemetria i zegar 10 ms; klient i kontroler zamknięte.
To nie zastępuje lokalnego smoke jazdy na komputerze każdej osoby. Wszyscy
używają jednego nowego commita obu branchy i zapisują hash; pełny start
od zera. Stary zamrożony checkout służy tylko starym checkpointom.

## Instalacja u kolegi

Użyj brancha `codex/tmrl-algorithm-runs` w osobnym katalogu. Jest to snapshot bieżącego
kodu wraz z lokalnymi zmianami; używaj tego samego commita u wszystkich.
Nie podmieniaj go na wersję biblioteki z PyPI. Wymagany Windows, GPU NVIDIA
ze sterownikiem zgodnym z dołączonym środowiskiem CUDA, Trackmania i Openplanet.

```powershell
git clone --branch codex/tmrl-algorithm-runs https://github.com/TrackmaniaRL/TrackmaniaRL.git
cd TrackmaniaRL
```

1. Zainstaluj uv, a w katalogu repozytorium wykonaj `uv sync --group dev`.
2. Skonfiguruj Openplanet School Mode, plugin TrackmaniaRL Connect / SAC_GetData
   i wirtualny gamepad zgodnie z `readme/trackmania.md`.
3. Otwórz dołączoną mapę `my-trackmania-agent/maps/trackmaniarl-test.Map.Gbx`
   w edytorze w trybie walidacji. Geometria jest już w paczce.
4. Utwórz własny prywatny `.env` z `WANDB_API_KEY=twoj_klucz`.
   Branch nie zawiera klucza Jakuba. Konto musi mieć dostęp do projektu zespołu.
5. Ustaw w PowerShell `$env:WANDB_ENTITY = 'dsc-pjatk-warsaw'`.
   Jeśli nie masz dostępu, ustal go z Jakubem przed startem.
6. Sprawdź CUDA: `uv run python -c "import torch; print(torch.cuda.is_available())"`.
   Wynik musi być `True` dla tych konfiguracji.
7. Sprawdź połączenie: `uv run trackmaniarl track check` oraz test bez gry:
   `uv run python -m experiments.tmrl_test_comparison.check`.
8. Bez działającego treningu, na załadowanej mapie zmierz lokalne sterowanie:
   `uv run trackmaniarl track check-steering --output artifacts/tmrl-test-comparison/steering-local.json`.
   Konfiguracje wymagają tego pliku. Nie kopiuj krzywej innej osoby; po zmianie
   ustawień kontrolera zmierz ją ponownie. Patrz [NIGHT_QUEUE.md](NIGHT_QUEUE.md).

Launcher przed każdym seedem sprawdza UID, restartuje walidację i wymaga
gotowego gracza oraz telemetrii. Kończy ten kontroler przed startem treningu;
nie uruchamiaj go obok innej jazdy. Chroni to przed brakiem ramek na ekranie
wyniku poprzedniego seeda. Błąd sprawdzenia zatrzymuje kolejkę.
Launcher sprawdza także działające procesy treningu i ewaluacji oraz odmawia
startu, jeśli katalog runu już istnieje. Wznowienie checkpointu wymaga osobnego
polecenia; ponowne uruchomienie launchera nie nadpisuje istniejącej próby.
Tryb `-Pilot` uruchamia tylko seed 17 z budżetem pilota, zwykle około 2–3 h
plus restarty i uczenie; nie ma twardego limitu czasu ściennego.

Po pozytywnym lokalnym pilocie przypisanego algorytmu uruchom **jedno** polecenie:

```powershell
# Kamil:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 tqc
# Kuba P.:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 ppo
# Operator continuous SAC, dopiero po lokalnym smoke i kalibracji:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 sac
```

Każde polecenie wykonuje trzy seedy kolejno, od zera. Nie uruchamiaj dwóch
algorytmów naraz na jednej instancji gry. IQN i QR u Jakuba mają analogiczne
polecenia. Bezpieczne zatrzymanie: utwórz plik `artifacts/STOP-NAZWA_ALGORYTMU`.
Ponowne wykonanie skryptu nie wznawia checkpointów i zatrzyma się na istniejącym
katalogu runu. Po przerwaniu wznów konkretny seed według protokołu.

## Co zwrócić

Linki do trzech runów W&B oraz foldery tych runów z `artifacts/tmrl-test-comparison/`,
w tym checkpointy, manifesty i JSONL. Zachowaj hash commita, model GPU/CPU,
wersję sterownika, FPS gry i ustawienia grafiki. Sprzęt i obciążenie gry mogą
zmieniać timing sterowania, więc sprawdzamy rozkład odstępów decyzji na każdym
komputerze. Nie porównuj samego czasu ściennego bez informacji o sprzęcie.

Ocena końcowych checkpointów: 30 przejazdów według `README.md`, osobno dla
każdego seeda; najlepiej wszystkie checkpointy ocenić później na jednym komputerze.
W&B jest wspólnym podglądem metryk, lokalne pliki zachowują pełny zapis próby.
