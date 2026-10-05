# Naprawy PPO i SD-SAC â€” 5 paĹşdziernika 2026

UĹĽytkownik po zakoĹ„czeniu nocnej kolejki poleciĹ‚ â€žTo napraw to wszystkoâ€ť, nastÄ™pnie
â€žMoĹĽesz robiÄ‡ dĹ‚uĹĽej niĹĽ do 10 tylko spraw by PPO i DSAC poprawnie dziaĹ‚aĹ‚oâ€ť.
Ta bezpoĹ›rednia instrukcja pozwala kontynuowaÄ‡ naprawy i ograniczone testy po
wczeĹ›niejszych godzinach 10:24/10:34. Nie uruchamia miesiÄ™cznych treningĂłw
ani nie zmienia wspĂłlnej nagrody. Nowy STOP uĹĽytkownika nadal ma pierwszeĹ„stwo.
Pierwotna kolejka zakoĹ„czyĹ‚a wszystkie etapy 09:26:36 Europe/Warsaw;
jej runner, watchdog i procesy oceny zakoĹ„czyĹ‚y siÄ™. Nie wznawiamy jej etapĂłw.

## UkoĹ„czona kampania nocna

| Polityka seed17 | Mety greedy | Mediana ukoĹ„czonych | Ĺšrednia ukoĹ„czonych | Maksymalny krok |
| --- | --- | --- | --- | --- |
| SD-SAC target2 / beta0 | 0/10 | â€” | â€” | 50 ms |
| PPO entropy0,01 | 8/10 | 56,445 s | 56,585 s | 50 ms |
| PPO entropy0 | 7/10 | 57,880 s | 57,673 s | 50 ms |
| IQN | 29/30 | 49,400 s | 49,452 s | 50 ms |
| TQC | 29/30 | 44,300 s | 44,384 s | 60 ms |
| SAC | 30/30 | 44,500 s | 44,366 s | 50 ms |
| QR | 26/30 | 56,915 s | 57,124 s | 50 ms |

Wszystkie oceny majÄ… kompletne waĹĽne pomiary czasu i brak bĹ‚Ä™dĂłw kontrolera
oraz telemetrii. Skips pozostajÄ… jawnie raportowane, nie byĹ‚y kryterium odrzucenia.
Ostatnia QR: 33 253 waĹĽne pomiary, p99 50 ms, 7 306 pominiÄ™tych ramek (max 5),
SHA checkpointu `325152941fd7c0d1a1950ee4ef15c8e1b6f837290e6e77dc195d42420c598ac6`.
Dowody w `artifacts/tmrl-test-comparison/queue-overnight-tuning-20261005/`
oraz `tmrl-overnight-diag-qr-s17-benchmark-20261005T065741490719/evaluation.json`.

SD-SAC rozliczyĹ‚ 145 487 krokĂłw, 33 871 aktualizacji i credit0,75, skoĹ„czony
checkpoint oraz fingerprint. Tylko 7 met w 208 epizodach treningu i 0/10 w ocenie
nie speĹ‚niajÄ… bramki >=8/10. PeĹ‚ny launcher SD-SAC pozostaje zablokowany.
PPO porĂłwnano na obu skoĹ„czonych cp70: 143 360 **uczonych** krokĂłw,
70 rolloutupdates; oba `full_training_complete=false`. Entropy0 ma medianÄ™
2,54% wolniejszÄ… i niĹĽszy odsetek met, wiÄ™c zachowujemy entropy0,01.
Oceny jednej polityki/seeda nie dowodzÄ… powtarzalnoĹ›ci uczenia 17/29/43
ani gotowoĹ›ci do celu 37 s. BrakujÄ…ce peĹ‚ne treningi nie sÄ… â€žpominiÄ™tymiâ€ť
etapami nocy â€” nigdy nie byĹ‚y w autoryzowanym planie.

## Naprawiony start i timing PPO

Pierwszy reset na ekranie mety prĂłbowaĹ‚ czytaÄ‡ telemetriÄ™, zanim wysĹ‚aĹ‚ restart.
Na tym ekranie gra moĹĽe przestaÄ‡ przesyĹ‚aÄ‡ ramki. Teraz restart poprzedza odczyt,
stare poĹ‚Ä…czenie jest zamykane, a reset wymaga nowej, aktywnej ramki z poczÄ…tku
wyĹ›cigu. ZamkniÄ™cie klienta dziaĹ‚a takĹĽe, gdy zamkniÄ™cie kontrolera zgĹ‚osi bĹ‚Ä…d.

Rzeczywisty `environment.reset` **z nowego edytowalnego kodu** zaliczony
09:32:58 Warsaw: wĹ‚aĹ›ciwy UID `oqIJ5rQDRrNwLPTh9H2p_W4tLof`, race_time10ms,
33 pola, success=true, timeout=false, zamkniÄ™cie w finally; bez uczenia.
DowĂłd: `queue-overnight-tuning-20261005/new-source-live-reset.json`.

PPO rozgrzewa obliczenia na syntetycznej obserwacji **przed resetem gry**.
Deterministyczna rozgrzewka nie zuĹĽywa RNG uĹĽywanego do dziaĹ‚aĹ„ ani nie zmienia
wag; pipeline jest nastÄ™pnie resetowany. Cykliczny GC jest odkĹ‚adany tylko na
czas rolloutĂłw, po ktĂłrych i tak nastÄ™puje reset. Stan GC jest przywracany
takĹĽe przy wyjÄ…tku; ciÄ…gĹ‚e rollouty zachowujÄ… dotychczasowe zachowanie.

PorĂłwnanie bez gry, faktyczny CUDA/GNN/Simba/PPO, 1 800 decyzji:
przed zmianÄ… median18,46ms/max551,31ms/1 ponad100ms; po rozgrzewce i odĹ‚oĹĽeniu GC
median17,65ms/max28,64ms/0 ponad100ms. Dowody `ppo-inference-before-fix.json`
i `ppo-inference-after-fix.json`. To nie usuwa potrzeby sprawdzenia timingĂłw
w grze: dotychczasowe uczenie miaĹ‚o skoki530/540ms, w tym rzadkie zakĹ‚Ăłcenia OS.

## SD-SAC: poprawne odniesienie stabilizacji i nowa hipoteza

Dotychczasowa implementacja jest wariantem SD-SAC z entropiÄ… modelu target,
co dokumentowano juĹĽ wczeĹ›niej. SD-SAC zapisuje entropiÄ™ **polityki zbierajÄ…cej
dane** przy przejĹ›ciu i porĂłwnuje z niÄ… aktualnÄ… entropiÄ™. Dodano jawny tryb
`entropy_penalty_reference: behavior`, zapis entropii podczas pojedynczej
decyzji i kolacjÄ™ przez replay. BrakujÄ…ce, niezgodne lub nieskoĹ„czone dane
sÄ… odrzucane; nie zastÄ™pujemy ich cichym odniesieniem do innej polityki.
DomyĹ›lny `target_policy` pozostaje dla zgodnoĹ›ci biblioteki. WspĂłĹ‚czynnik beta
jest mnoĹĽnikiem MSE zgodnie z kodem autorĂłw (ich wzĂłr w publikacji ma dodatkowe1/2).

ĹąrĂłdĹ‚a: [artykuĹ‚ SD-SAC, sekcja5.1](https://arxiv.org/html/2209.10081#S5.SS1),
[implementacja autorĂłw](https://github.com/coldsummerday/SD-SAC/blob/main/src/libs/discrete_sac.py).

Poprzedni pilot beta0 miaĹ‚ ten skĹ‚adnik wyĹ‚Ä…czony, wiÄ™c rozbieĹĽnoĹ›Ä‡ nie tĹ‚umaczy
samodzielnie jego poraĹĽki. Odczyt jego checkpointu/replay na oryginalnym frozen8f
potwierdziĹ‚ fingerprint i wykazaĹ‚ zgodnoĹ›Ä‡ actor/critic dla wszystkich64
ostatnich stanĂłw startowych, entropiÄ™3,10nats i alpha0,0187. Na512 stanach
zablokowanie gradientu przez Q-clip wystÄ…piĹ‚o w0,2% prĂłbek. To ogranicza
hipotezy, nie dowodzi przyczyny lokalnego optimum.

Nowy **Ĺ›wieĹĽy**, ograniczony pilot sprawdzi target0,8nats/beta0,5 z odniesieniem
do zapisanej entropii zachowania. Nagroda, 78 dziaĹ‚aĹ„, model, seed17 i budĹĽet
145408 pozostajÄ… wspĂłlne. Bramka ustalona przed testem: peĹ‚ne rozliczenie
budĹĽetu/credit, skoĹ„czony cp/fingerprint,10 kompletnych prĂłb, >=8/10 met,
waĹĽny timing kaĹĽdej, max<=100ms, bez bĹ‚Ä™dĂłw i z raportem skips. Dopiero
zaliczenie moĹĽe zmieniÄ‡ peĹ‚ne konfiguracje SD-SAC17/29/43 i zdjÄ…Ä‡ blokadÄ™.

## Weryfikacja kodu i dalszy test

106 testĂłw regresji/kontraktĂłw przeszĹ‚o, w tym powrĂłt checkpointu/replay,
gradient stabilizacji, zgodnoĹ›Ä‡ metadanych z transition IDs, reset i cleanup,
RNG rozgrzewki, GC przy wyjÄ…tkach oraz oba testy blokady PowerShell wczeĹ›niej
odĹ‚oĹĽone z powodu zajÄ™tego mutexu. Ruff i mypy(8 plikĂłw ĹşrĂłdĹ‚owych) przechodzÄ….
41 konfiguracji porĂłwnania ma poprawny schemat. Standardowy CPUvalidator SD-SAC
w trybie behavior wykonaĹ‚ update i checkpoint roundtrip. Standardowy CPUvalidator PPO wykonaĹ‚ peĹ‚ny rollout2048/update i checkpoint
roundtrip, bez wczeĹ›niejszego przepeĹ‚nienia replay. Ĺ»aden validator nie sterowaĹ‚ grÄ….

Stare runtime8f/d0 i checkpointy sÄ… zachowane. Nowe piloty rozpoczynajÄ… od zera
na nowym zamroĹĽonym commicie; nie wznowimy starych checkpointĂłw na zmienionym kodzie.
MiesiÄ™czne starty nadal wymagajÄ… lokalnej kalibracji/smoke oraz wspĂłlnego nowego
commita i jawnego rÄ™cznego startu. Nie deklarujemy ich gotowoĹ›ci przed live wynikami.

## Nazwa SD-SAC

Na bezpośrednie polecenie użytkownika nazwa projektu to **SD-SAC**. Nowe
konfiguracje, manifest, scaffold i launchery używają `sd-sac`. Starsze wejścia
`dsac`/`discrete-sac` i import `DiscreteSACConfig` są aliasami zgodności.
Nie zmieniamy identyfikatorów zapisanych runów, checkpointów i historycznych
dowodów ani dosłownych cytatów instrukcji użytkownika. Stare runtime8f/d0
pozostają zamrożone. Blokada niezakwalifikowanego pełnego startu obejmuje
zarówno nową nazwę, jak i oba aliasy; wcześniejsze pliki STOP nadal są respektowane.

Testy nazewnictwa obejmują SD-SAC oraz oba stare aliasy, generowanie scaffold,
model telemetryczny i vision, update oraz wznowienie checkpointu. Równoległe
zestawy pytest początkowo współdzieliły `.pytest-cache/tmp`, co usunęło
artefakt innego testu. Powtórzenie52 testów w osobnym katalogu tymczasowym
przeszło; nie przypisujemy tego konfliktu zapisowi modelu. Pozostałe grupy
127 i24 testów również przeszły.
