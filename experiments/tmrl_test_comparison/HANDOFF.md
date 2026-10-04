# Podział eksperymentów

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
