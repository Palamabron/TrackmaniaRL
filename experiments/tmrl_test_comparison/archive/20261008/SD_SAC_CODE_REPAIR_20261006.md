# SD-SAC: poprawki kodu po zatrzymaniu — 6 października 2026

Status: **kod poprawiony; jakość jazdy nieweryfikowana; nowe próby zabronione do zgody człowieka**.
Polecenie „to napraw to wszystko” zezwala na poprawki kodu. Nie odwołuje wcześniejszego
zakazu nowego treningu, ewaluacji, testu jazdy ani pilota. Automatyzacja pozostaje PAUSED,
STOP kolejki actorlr0009 zachowany. Nie utworzono ani nie uruchomiono nowego runtime/kolejki.

## Co naprawiono

- Checkpoint ocenionej polityki zachowuje `actor_learning_rate`, zamiast resetować
  optymalizator aktora do tempa krytyka. Wczytanie nowego checkpointu sprawdza konfigurację
  i rzeczywiste tempa trzech optymalizatorów przed zmianą wag. Nie można niejawnie zmienić
  celu aktora/temperatury przy wznowieniu. Starego checkpointu nie wznawiano.
- Aktor kategoryczny udostępnia float32 log-softmax. SD-SAC korzysta z niego w celu,
  bootstrapie i pomiarach entropii zamiast obcinać logarytmy małych prawdopodobieństw.
  Kanoniczne modele z interfejsem tylko `probabilities` pozostają obsługiwane.
- Temperatura ma osobne `entropy_learning_rate` oraz opcjonalne dodatnie granice alpha.
  Projekcja log-alpha działa po aktualizacji; stan spoza granic lub niereprezentowalny
  jako dodatnie finite float32 jest odrzucany przy wczytaniu. `state/alpha_used` wskazuje
  temperaturę używaną w kroku, a `state/alpha` tę po regulacji. Walidacja odrzuca NaN/Inf
  w parametrach i niemożliwy cel entropii większy od log liczby akcji.
- Dodano **jawny opcjonalny wariant** `actor_objective: soft_q_forward_kl`: cross-entropy
  do odłączonego softmax z centrowanych Q/alpha. Zachowuje gradient do pomijanych akcji,
  również gdy ich prawdopodobieństwo pod reprezentacją float32 wynosi zero. Nie jest
  kanonicznym SD-SAC ani dowodem poprawności krytyka. Domyślnie nadal `sac`; żadna
  konfiguracja uruchomionej próby nie została przełączona na wariant. Kara entropii
  pozostaje jawnie konfigurowana i nie została arbitralnie usunięta.
- Logowanie obejmuje błąd celu entropii, oba KL wobec soft-Q, regret wybranej akcji,
  zgodność rankingów krytyków, TD bias/RMSE, clipping i faktyczną blokadę gradientu,
  liczbę końcowych stanów oraz ich osobny błąd TD. Zgodność actor/Q nie jest bramką jazdy.
- SD-SAC odrzuca zwykły `n_step>1` w walidacji runtime oraz oznaczonych batchach:
  agregacja samych nagród pomija pośrednią entropię soft return. Generator telemetryczny
  i obrazowy SD-SAC oraz przykład w dokumentacji teraz wymagają `n_step=1`.
  Poprzednie piloty już używały 1; ten błąd konfiguracji nie wyjaśnia ich porażek.

Domyślne tempo temperatury dziedziczy tempo krytyka, alpha nie ma narzuconych granic,
cel aktora jest kanoniczny. Dodanie mechanizmów kontroli nie oznacza, że dowolne nowe
wartości tych parametrów zostały potwierdzone jako skuteczne.

## Co wykazał odczyt istniejących danych

Nowy moduł `sd_sac_calibration.py` porównuje Q wybranych akcji z kompletnymi
zapisanymi epizodami. Soft return uwzględnia entropię **następnych** stanów, kończy
bootstrap przy prawdziwym zakończeniu, wyklucza niekompletne/przerwane epizody.
Nie wnioskuje o akcjach niewybranych. Dawna polityka zachowania różni się od bieżącej:
porównanie pełnych epizodów jest proxy, nie dowodem kalibracji on-policy. Stan terminalny
ma bezpośredni cel równy ostatniej nagrodzie i nie wymaga założenia o dalszej polityce.

Odczyt cp25112 i ostatnich danych wykonano z **oryginalnego frozen c72591ed**,
wyłącznie przez model inference i odczyt replay. Zero kroków optymalizatora, zero
aktualizacji learnera, bez środowiska/kontrolera. SHA/fingerprint zgodne przed/po.
Wybrano 33 ostatnie epizody: 31 kompletne (19034 stany), 2 wykluczone.

| Próbka | Średnie przewidywane Q | Zapisany cel/proxy | Błąd średni | RMSE |
| --- | ---: | ---: | ---: | ---: |
| Terminal, 31 stanów | 1.6086 | −2.0518 (rzeczywista ostatnia nagroda) | 3.6604 | 4.1004 |
| Wszystkie kompletne stany | 6.5527 | 3.8305 (behavior soft return proxy) | 2.7222 | 5.2691 |
| Pełny hamulec, 649 stanów | 5.8423 | 0.2452 (proxy) | 5.5972 | 6.7875 |
| Start, 31 stanów | 7.0400 | 5.3971 (proxy) | 1.6430 | 4.6318 |

To dane treningowe, nie held-out. Potwierdzają błąd predykcji końca epizodu w starym
modelu; nie dowodzą, że nowy sposób dopasowania aktora rozwiąże jazdę. Stary model ma
nadal entropy0.271, alpha0.000935, zgodność actor/Q7.62% w wcześniej zbadanych 1024 stanach.
Nie zmodyfikowano jego wag. Dowody w BASE/sd-sac-stopped-analysis-20261006:
`calibrate_saved_returns.py`, `recorded-return-calibration.json`, poprzedni
`saved-checkpoint-inspection.json`. Zachowano SHA checkpointu
`37188c52fc549c26f4c31b792678a10fa3308b1cd32666c76dd7d0342999577f`.

## Sprawdzenia i ograniczenia

91 testów kodu na syntetycznych danych CPU passed, 2 istniejące wielokrotne pętle
uczenia na syntetycznych danych pominięte. Po poprawce generatora 7 testów jego
tożsamości/konfiguracji ponownie passed. Sprawdzono analityczny gradient wariantu przy
logitach +1000/−1000, kierunek i granice regulacji alpha, brak grafu krytyka w kroku aktora,
kontrolę tempa optymalizatorów i opcji checkpointu, raport końcowego TD, wykrycie blokady
gradientu przez clipping, matematykę soft return i odrzucenie niepełnych epizodów.
Ruff i mypy zmienionych modułów passed. Testy kodu nie dotykały zapisanych wag ani gry.

**Full SD BLOCKED. Nie ma nowego wyniku jazdy.** Błąd wartości w zapisanym modelu
nie został magicznie usunięty przez zmianę kodu. Po osobnej zgodzie należy najpierw
zweryfikować kalibrację krytyka (zwłaszcza końców epizodów), następnie dobór regulacji
entropii i celu aktora, w świeżych rozdzielonych próbach. Bramka pozostaje >=8/10 wraz
z pełnym/drained/accounted/finite checkpointem, zgodnym źródłem/SHA, UID, timingiem
i raportem błędów/skips. Wznowienie starego modelu na nowym kodzie jest zabronione.
QR29/30, mediana54.3s pozostaje zachowanym PASS. Nie ma automatycznego pełnego startu.
