# Status algorytmów i interpretacja wyników

Standardowe konfiguracje pozostają dla IQN, Q, QR, FQF, SAC, TQC, REDQ i PPO.
Przydzielona kampania używa IQN, QR, SAC, TQC i PPO. Q/FQF/REDQ nie mają przydziału.
SD-SAC jest experimental: zachowujemy implementację i dowody, lecz normalny
manifest, pilot scheduler i launchery go odrzucają, także pod aliasami `dsac`
i `discrete-sac`. Oddzielny `experimental-manifest.json` nie stanowi zgody startu.

Rozdzielamy dyskretny i ciągły zestaw akcji; wspólny enkoder nie oznacza identycznych
modeli ani kosztów uczenia. Zachowane wyniki i ograniczenia PPO: [READINESS.md](READINESS.md).
Nowe budżety i fingerprinty nie zezwalają na resume starych checkpointów.
Brak poprawek wspólnej nagrody/modelu/GNN/replayu w ramach wycofania SD-SAC.

Aktualny plan: [MULTI_COMPUTER_TRAINING.md](MULTI_COMPUTER_TRAINING.md).
SD-SAC jest **experimental**, wyłączony ze standardowych kolejek; scheduler
napraw jest **PAUSED**. Raport i pełny prompt dla Fable 5.1:
[SD_SAC_FABLE_5_1_REPORT.md](SD_SAC_FABLE_5_1_REPORT.md).

Historia: [archiwum ALGORITHM_AUDIT.md](archive/20261008/ALGORITHM_AUDIT.md).
