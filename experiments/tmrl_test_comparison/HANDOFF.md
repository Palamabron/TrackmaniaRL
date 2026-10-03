# Podział eksperymentów

| Osoba | Algorytm | Pełne treningi |
| --- | --- | --- |
| Jakub | IQN i QR | każdy: seedy 17, 29, 43 |
| Borys | discrete SAC | seedy 17, 29, 43 |
| Kamil | TQC | seedy 17, 29, 43 |
| Kuba P. | PPO | seedy 17, 29, 43 |

Aktualna decyzja przed pełnym startem: [READINESS.md](READINESS.md).
IQN i QR zakończyły piloty. Discrete SAC wymaga dodatkowej diagnostyki;
TQC i PPO muszą jeszcze przejść ocenę pilotów.
Restarty, obliczenia i aktualizacje PPO wydłużą czas. Pełnych treningów nie
uruchamiamy automatycznie po pilotach. Przed przekazaniem do długich prób
sprawdzamy każdy algorytm: aktualizacje o skończonym lossie, zmiana polityki,
ukończony budżet, poprawny zapis końcowego checkpointu, metryki w W&B,
stabilne sterowanie i brak błędów telemetryki. Pilot nie musi ukończyć mapy,
ale sam działający proces nie jest jeszcze pozytywnym wynikiem testu.

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

Po pozytywnym lokalnym pilocie przypisanego algorytmu uruchom **jedno** polecenie:

```powershell
# Borys:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 discrete-sac
# Kamil:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 tqc
# Kuba P.:
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 ppo
```

Każde polecenie wykonuje trzy seedy kolejno, od zera. Nie uruchamiaj dwóch
algorytmów naraz na jednej instancji gry. IQN i QR u Jakuba mają analogiczne
polecenia. Bezpieczne zatrzymanie: utwórz plik `artifacts/STOP-NAZWA_ALGORYTMU`.
Ponowne wykonanie skryptu rozpoczyna nowe próby, a nie wznawia checkpointów.
Po przerwaniu ustal wznowienie konkretnego seeda zamiast ponownie odpalać całość.

## Co zwrócić

Linki do trzech runów W&B oraz foldery tych runów z `artifacts/tmrl-test-comparison/`,
w tym checkpointy, manifesty i JSONL. Zachowaj hash commita, model GPU/CPU,
wersję sterownika, FPS gry i ustawienia grafiki. Sprzęt i obciążenie gry mogą
zmieniać timing sterowania, więc sprawdzamy rozkład odstępów decyzji na każdym
komputerze. Nie porównuj samego czasu ściennego bez informacji o sprzęcie.

Ocena końcowych checkpointów: 30 przejazdów według `README.md`, osobno dla
każdego seeda; najlepiej wszystkie checkpointy ocenić później na jednym komputerze.
W&B jest wspólnym podglądem metryk, lokalne pliki zachowują pełny zapis próby.
