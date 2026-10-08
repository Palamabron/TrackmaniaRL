# Decyzje o ustawieniach

Nowa kampania zachowuje ustawienia standardowych algorytmów, zmienia budżet na
8 192 000 kroków i nadaje nowe identyfikatory. Nie miesza wyników z historycznym
full 2 048 000. PPO dostaje horyzont harmonogramu LR wynikający z dłuższego budżetu.

SD-SAC nie ma zatwierdzonej poprawki. Szybszy actor dał 0/10 w grze, a ważenie
terminali poprawiało część błędów kosztem nieakceptowalnego driftu innych stanów.
Kończymy automatyczne siatki loss/LR/temperature/margin/weights i resety Adama.
Propozycja obserwowalności czasu pozostaje niezaimplementowana, poza zakresem
nowej kampanii. Dalsza praca nad SD-SAC wymaga osobnego zadania i jawnego zakresu.

Aktualny plan: [MULTI_COMPUTER_TRAINING.md](MULTI_COMPUTER_TRAINING.md).
SD-SAC jest **experimental**, wyłączony ze standardowych kolejek; scheduler
napraw jest **PAUSED**. Raport i pełny prompt dla Fable 5.1:
[SD_SAC_FABLE_5_1_REPORT.md](SD_SAC_FABLE_5_1_REPORT.md).

Historia: [archiwum TUNING.md](archive/20261008/TUNING.md).
