# Wspólne treningi na tmrl-test

Pełna instrukcja: [HANDOFF.md](experiments/tmrl_test_comparison/HANDOFF.md).
Protokół pomiarów: [README.md](experiments/tmrl_test_comparison/README.md).

| Kto | Algorytm | Seedy |
| --- | --- | --- |
| Jakub | IQN + QR | 17, 29, 43 dla każdego |
| Kolega 1 | discrete SAC | 17, 29, 43 |
| Kolega 2 | TQC | 17, 29, 43 |
| Kolega 3 | PPO | 17, 29, 43 |

**Przed pełnym startem czekamy na lokalne piloty u Jakuba.** IQN już wykonuje
aktualizacje i ukończył mapę w treningu. QR, discrete SAC, TQC i PPO mają
zaplanowane po 145 408 kroków — około 2 h jazdy każdy, więcej z narzutami.
Nie są jeszcze zatwierdzone jako przetestowane w grze.

Branch zawiera snapshot lokalnej biblioteki używanej przez te eksperymenty,
konfiguracje oraz mapę i geometrię. U wszystkich używamy tego samego commita.
Nie zawiera `.env`, kluczy, checkpointów ani wyników. Każdy używa własnego
klucza W&B z dostępem do projektu `dsc-pjatk-warsaw/my-trackmania-agent`.

Po instalacji i sprawdzeniu gry według HANDOFF każdy kolega uruchamia swój
algorytm jednym poleceniem, np.:

```powershell
powershell -ExecutionPolicy Bypass -File experiments/tmrl_test_comparison/run_assigned.ps1 tqc
```

To uruchamia trzy pełne treningi TQC kolejno. Dla pozostałych osób zamień `tqc`
na `discrete-sac`, `ppo`, `iqn` lub `qr`. Każdy pełny trening ma 2 048 000 kroków;
to około 28,4 h samej jazdy. Nie uruchamiaj kilku procesów sterujących tą samą grą.
