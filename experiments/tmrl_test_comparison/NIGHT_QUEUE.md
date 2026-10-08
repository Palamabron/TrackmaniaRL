# Kolejki i automatyzacje — stan aktualny

Stare kolejki SD-SAC są zamknięte i wycofane. Nie restartuj ich launcherów.
Heartbeat `trackmania-nocne-piloty-i-gotowo-trening-w` jest PAUSED; zachowana
częstotliwość 15 minut nie oznacza aktywnego monitoringu. Nie utworzono nowej
automatyzacji ani nie uruchomiono gry w ramach przygotowania kampanii.

Nowa kolejka: `campaign.json`, 15 runów w `configs/weeks/`. Kolejność i nadzór
lokalny opisuje aktualny plan. STOP/niekompletny zapis/błąd kończy kolejkę,
bez automatycznego restartu. Stare mutable pointers i stan diagnozy wycofano
z zachowaniem kopii w lokalnym `artifacts/tmrl-test-comparison/sd-sac-retired-20261008/`.
Dowód wycofania jest w `evidence/sd-sac-retired-20261008/retirement.json`.

Aktualny plan: [MULTI_COMPUTER_TRAINING.md](MULTI_COMPUTER_TRAINING.md).
SD-SAC jest **experimental**, wyłączony ze standardowych kolejek; scheduler
napraw jest **PAUSED**. Raport i pełny prompt dla Fable 5.1:
[SD_SAC_FABLE_5_1_REPORT.md](SD_SAC_FABLE_5_1_REPORT.md).

Historia: [archiwum NIGHT_QUEUE.md](archive/20261008/NIGHT_QUEUE.md).
