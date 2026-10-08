# Treningi na kilku komputerach

SD-SAC jest **experimental** i nie uczestniczy w tej kampanii. Jego automatyczne
naprawy są wstrzymane. Przygotowano 15 niezależnych runów; treningów nie uruchomiono.

| Osoba | Algorytmy kolejno | Seedy każdego |
| --- | --- | --- |
| Jakub | QR, IQN | 17, 29, 43 |
| Borys | ciągły SAC | 17, 29, 43 |
| Kamil | TQC | 17, 29, 43 |
| Kuba P. | PPO, po lokalnym pilocie | 17, 29, 43 |

Nowy profil ma 8 192 000 kroków/seed: nominalnie około 14 dni jazdy na algorytm
z trzema seedami, około 28 dni u Jakuba. Sprzęt, uczenie i restarty wydłużą czas.
Historyczny profil full 2 048 000 pozostaje oddzielnym protokołem.

[Pełny plan, instalacja, późniejszy start, STOP i przerwy](experiments/tmrl_test_comparison/MULTI_COMPUTER_TRAINING.md).
[Gotowość i ograniczenia wyników](experiments/tmrl_test_comparison/READINESS.md).
[Raport i kompletny prompt dla Fable 5.1](experiments/tmrl_test_comparison/SD_SAC_FABLE_5_1_REPORT.md).

Najpierw w czystym checkoutcie identycznego commita sprawdź swój plan bez jazdy:

```powershell
powershell -NoProfile -File experiments/tmrl_test_comparison/run_campaign.ps1 -Worker borys
```

Podstaw `jakub`, `borys`, `kamil` lub `kuba-p`. Dopiero opisane w pełnym planie
lokalne sprawdzenia i jawny `-Launch` rozpoczynają trening. Nie uruchamiaj kilku
kontrolerów jednej gry. Nie kopiuj `.env`, starych checkpointów ani cudzej kalibracji.
