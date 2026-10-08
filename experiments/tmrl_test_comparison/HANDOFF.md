# Przekazanie treningów na cztery komputery

| Osoba | Zadanie | Seedy |
| --- | --- | --- |
| Jakub | QR, następnie IQN | 17, 29, 43 każdego |
| Borys | ciągły SAC | 17, 29, 43 |
| Kamil | TQC | 17, 29, 43 |
| Kuba P. | PPO, po lokalnym pilocie | 17, 29, 43 |

Pełna instrukcja instalacji, budżetu, poleceń bez jazdy, późniejszego startu,
STOP, przerwy, backupu i oddawanych wyników jest w aktualnym planie poniżej.
Domyślne `run_campaign.ps1 -Worker ...` tylko pokazuje kolejkę; dopiero `-Launch`
uruchamia grę. Przygotowano 15 nowych runów, żadnego nie uruchomiono.
Wszyscy pracują na tym samym czystym commicie brancha `codex/tmrl-algorithm-runs`.
Nie kopiuj `.env`, checkpointów ani kalibracji autora do nowego treningu.

Aktualny plan: [MULTI_COMPUTER_TRAINING.md](MULTI_COMPUTER_TRAINING.md).
SD-SAC jest **experimental**, wyłączony ze standardowych kolejek; scheduler
napraw jest **PAUSED**. Raport i pełny prompt dla Fable 5.1:
[SD_SAC_FABLE_5_1_REPORT.md](SD_SAC_FABLE_5_1_REPORT.md).

Historia: [archiwum HANDOFF.md](archive/20261008/HANDOFF.md).
