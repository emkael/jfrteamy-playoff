
JFR Teamy - play-off - plik konfiguracyjny
==========================================

Ogólny format
-------------

Plik konfiguracyjny jest formatu JSON - a to oznacza na przykład, że trzeba pilnować backslashów wewnątrz łańcuchów znaków.
Na przykład - backslashe w konfiguracji logo nagłówka są podwojone. Szczególnie należy na to uważać przy podawaniu ścieżek do pliku wyjściowego.


Opcje ogólne
------------

Konfiguracja składa się, po kolei, z:
 - pola `"output"`: ścieżki do pliku, do którego będzie generowana drabinka.
   Polecam ścieżkę bezwzględną do katalogu WWW turnieju.
   W ścieżce musi znajdować katalog `sklady/`, do którego kopiowany jest JavaScript `playoff.js`
 - sekcji `"page"`: ustawień strony
   + `"title"` - tytuł (`<title>` HTMLa)
   + `"favicon"` - adres fawikony
   + `"logoh"` - nagłówek, jak w tabeli admin bazy turnieju
   + `"refresh"` - parametr odświeżania strony drabinki: `0` = wyłączone, liczba naturalna = interwał odświeżania, w sekundach
   + `"width"` i `"height"` - wymiary (w pikselach) miejsca rezerwowanego dla każdego meczu w widoku drabinki (`"width"` bezpośrednio wpływa na rozmieszczanie kolumn, wewnątrz każdej z kolumn mecze rozmieszczane są równomiernie, w zależnie od ich liczby)
   + `"margin"` - odstęp między w/w miejscem (minimalny - jak widać, w przypadku mniejszej liczby meczów w fazie, odstępy się dopasują)
   + `"starting_position_indicators"`, `"finishing_position_indicators"` - włączają znaczniki miejsc początkowych/końcowych, wynikających ze zdefiniowanego schematu
   + słownik `"team_boxes"` przechowuje opcjonalne ustawienia wyświetlania nazw teamów:
     * `"label_length_limit"` - maksymalna liczba znaków wyświetlanych jako skrócona nazwa drużyn(y) w schemacie (domyślnie `0` = brak limitu)
     * `"auto_carryover"` - jeśli dla teamów określono wynik początkowy (np. pobrano z wyników turnieju), włącza automatyczne wyliczanie carry-over dla meczów, których jeszcze nie rozegrano, a obie drużyny są już znane (wartość w procentach, domyśnie `0` = nie wylicza)
     * `"league_carryovers"` - dla meczów jeszcze nierozegranych, wyświetlanie wyniku z zaokrągleniem "ligowym": do 0.1 w górę chyba że wyjdzie liczba całkowita, to w dół (domyślnie `0` = wyłączone)
     * `"predict_teams"` - flaga, jeśli włączona (`1`), w kolejnej fazie wypełniane są nazwy drużyn prowadzących/przegrywających w trwających meczach tak, jakby mecz miał się skończyć aktualnym wynikiem (etykiety takich drużyn mają nadaną osobną klasę CSS)
     * `"label_separator"` - ciąg rozdzielający skrócone nazwy drużyn wyświetlane na schemacie (domyślnie ` / `)
     * `"label_placeholder"` - ciąg wyświetlany w miejsce nieznanej drużyny (domyślnie `??`)
     * `"label_ellipsis"` - ciąg wyświetlany na końcu skróconej etykiety teamów, gdy ustawienie `label_length_limit` ją skróciło (domyślnie `(...)`)
     * `"name_separator"` - ciąg rozdzielający pełne nazwy teamów w etykiecie po najechaniu na skrócone nazwy w schemacie (domyślnie `<br />`)
     * `"name_prefix"` - ciąg poprzedzający każdą pełną nazwę teamów w etykiecie po najechaniu (domyślnie wcięcie `&nbsp;&nbsp;`)
     * `"sort_eligible_first"` - flaga włączająca wyświetlanie teamów zakwalifikowanych do danej fazy (tj. z zakończonym meczem bieżącej fazy) przed teamami z trwających meczów (domyślnie włączona)
 - sekcji `"canvas"`: ustawień rysowania linii
   + `"winner_colour"`, `"loser_colour"` - kolory linii zwycięzców i przegranych
   + `"place_winner_colour"`, `"place_loser_colour"` - kolory linii łączących początkowe miejsca drużyn z pierwszymi meczami (`loser` - drużyny mogące zagrać w więcej niż jednym meczu, czyli wybierane)
   + `"finish_winner_colour"`, `"finish_loser_colour"` - kolory linii łączących końcowe miejsca drużyn z ich ostatnimi meczami
   + `"winner_h_offset"`, `"winner_v_offset"` - marginesy (poziomy i pionowy) rysowania linii zwycięzców (odpowiednio: pionowych i poziomych, względem środka obszaru)
   + `"loser_h_offset"`, `"loser_v_offset"` - analogiczne marginesy rysowania linii przegranych
   + `"place_winner_h_offset"`, `"place_winner_v_offset"`, `"place_loser_h_offset"`, `"place_loser_v_offset"`, `"finish_winner_h_offset"`, `"finish_winner_v_offset"`, `"finish_loser_h_offset"`, `"finish_loser_v_offset"` - marginesy rysowania linii łączących mecze z miejscami początkowymi/końcowymi
   + `"box_positioning"`: możliwość ręcznego ustawienia pozycji każdego meczu - słownik indeksowany tekstowymi identyfikatorami meczów, z wartościami liczbowymi: pojedyncza wartość = pozycja w pionie w pikselach, w ramach fazy meczu, tablica dwóch wartości: dowolna pozycja w pikselach
   + `"fade_boxes"`: czas po najechaniu kursorem na mecz, po którym mecze (i linie) niepowiązane z danym meczem są wygaszane (`0` = efekt wyłączony, wszystkie linie i mecze zawsze widoczne)
 - sekcji `"database"`, zawierającej ustawienia połączenia bazy danych
 - sekcji `"goniec"`, zawierającej ustawienia Gońca (`"enabled"` przyjmuje wartości `0`/`1`)

Ustawienia bazy danych nie są wymagane, program potrafi sobie poradzić bez nich, jeśli do poszczególnych faz/meczów podano dostępne przez HTTP linki.

Ustawienia Gońca nie są wymagane, domyślnie jest on wyłączony, a przy włączeniu - domyślnie komunikuje się z `localhost` na porcie `8090`.

Tłumaczenia tekstów
-------------------

Program obsługuje możliwość ustawienia własnych łańcuchów znaków wyświetlanych w różnych miejscach wynikowej strony. Teksty te opcjonalnie określa sekcja `"i18n"` pliku konfiguracyjnego.

Domyślna postać wszystkich obsługiwanych łańcuchów to:

```
{
    "SCORE": "wynik",
    "FINAL_STANDINGS": "klasyfikacja końcowa",
    "STANDINGS_PLACE": "miejsce",
    "STANDINGS_TEAM": "drużyna",
    "STANDINGS_CAPTIONS": "legenda",
    "FOOTER_GENERATED": "strona wygenerowana",
    "SWISS_DEFAULT_LABEL": "Turniej o&nbsp;%d.&nbsp;miejsce"
}
```

Zdalne pliki konfiguracyjne
---------------------------

Sekcja `"remotes"` umożliwia zdefiniowanie zdalnych (dostępnych przez HTTP(S)) plików konfiguracyjnych, które są scalane z lokalną konfiguracją. Jest to tablica URLów.

Konfiguracja scalana jest per sekcja. Jeśli sekcja jest obecna w pliku lokalnym, nie jest zmieniana. Jeśli sekcja obecna jest w kilku plikach zdalnych, sekcje późniejsze nadpisują sekcje wcześniejsze.


Ustawienia teamów
-----------------

Dalej mamy sekcję `"teams"`. W niej definiujemy teamy w kolejności, wg której mają być rozdzielane miejsca (w sytuacjach "przegrani zajmują miejsca...").

Każdy team to tablica, kolejno: pełnej nazwy (tej, która MUSI się zgadzać z nazwami we wszystkich turniejach), skróconej nazwy, pliku flagi (opcjonalnie).

Jako czwarty element każdej tablicy można wpisać liczbę naturalną, która oznacza pozycję, jaką team ma zająć w końcowej klasyfikacji (tj. wpisanie tam liczby oznacza, że team od samego początku umieszczany jest na tej pozycji w klasyfikacji końcowej - np. jeśli nie uczestniczy w ogóle w play-off).

Co zrobić, gdy jest taki team, a turniej nie ma ustawionych obrazków z flagami? Ustawić flagę na `null` - nie zostanie wyświetlona.

Jako piąty element każdej tablicy można wpisać wynik początkowy drużyny, używany do automatycznego wyliczania carry-over (p. `"auto_carryover"` powyżej).


Ustawienia teamów - wariant pobierania z istniejącego turnieju
--------------------------------------------------------------

Sekcja `"teams"` może również być **obiektem**, określającym turniej (np. fazy zasadniczej), z którego zostanie pobrana lista teamów. Pobierane są: pełna nazwa, nazwa skrócona oraz nazwa pliku flagi.

Składa się z następujących pól:
 - `"database"` - nazwa bazy danych turnieju, z której pobierana jest lista teamów ALBO
 - `"link"` - URL do strony wyników (`PREFIXleaderb.html` dla JFR Teamy, `index.html` dla Tournament Calculatora) turnieju, dostępnej zdalnie
 - opcjonalne pole `"final_positions"` - tablica numerów miejsc, dla drużyn, które zakończyły rozgrywki (odpowiednik czwartego pola tablicy w tekstowej wersji listy teamów)
 - opcjonalne pole `"max_teams"` - wymusza pobranie tylko określonej liczby pierwszych teamów z tabeli
 - przy użyciu `"database"`: opcjonalne pole `"ties"` - tablica pełnych nazw drużyn w kolejności, w jakiej rozstrzygane powinny być remisy w VP w turnieju źródłowym

Miejsca w tabeli końcowej dla drużyn zdefiniowanych jako kończące rozgrywki będą zgodne z miejscami zajętymi w zdefiniowanym turnieju. Jeśli potrzeba zmapować te miejsca na inne miejsca klasyfikacji końcowej, należy użyć sekcji `"swiss"`, opisanej poniżej.

Program nie potrafi ich rozstrzygać samodzielnie remisów podczas pobierania wyników z bazy danych. Dla listy teamów pobranej ze strony wyników, zachowana jest kolejność na stronie (więc remisy rozstrzygnięte przez Teamy przed wygenerowaniem wyników).

Ustawienia teamów - aliasy
--------------------------

Jeśli zdarzy się, że w jakichś meczach, pobieranych ze stron WWW lub bazy danych, pełna nazwa teamu nie zgadza się z nazwą zefiniowaną na liście teamów, nazwy takie można zmapować na właściwe nazwy teamów.

Służy do tego sekcja `"team_aliases"`, będąca słownikiem, w którym:
 - kluczami są docelowe (tj. obecne w liście teamów) pełne nazwy teamów
 - wartościami są tablice nazw, które mają być mapowane na daną właściwą nazwę

Na przykład:

```
"team_aliases": {
    "SYNERGIA Lublin": ["Synergia Lublin", "Synergia", "SYNERGIA", "SYNERGIA  Lublin", "SYNERGIA Lublin "]
}
```

Wszystkie zdefiniowane w takim słowniku nazwy teamów będą rozpoznawane jako właściwe nazwy, obecne w liście teamów.

Ustawienia teamów - kolejność końcowa
-------------------------------------

W przypadku zdefiniowania zajmowania przez kilka teamów kilku pozycji końcowych w klasyfikacji, teamy szeregowane są według kolejności na wczytywanej (bądź określonej) liście teamów (np. pobranej z turnieju lub bazy danych).

Aby zmienić tę kolejność (bo np. nie zawsze rozstrzygnięcie kolejności końcowej opiera się o kolejność po fazie zasadniczej), można określić w konfiguracji sekcję `custom_final_order`.

Jest ona tablicą wartości: wartością może być łańcuch tekstowy - pełna nazwa teamu lub liczba - jego pozycja w pobranej liście teamów.

Ustawienia stylów klasyfikacji końcowej
---------------------------------------

Sekcja `"position_styles"` pozwala wyróżnić określone pozycje tabeli klasyfikacji końcowej, nadając im dowolnie zdefiniowaną klasę CSS.

Jest to tablica obiektów o następujących składowych:
 - `"class"` - nazwa klasy CSS ustawianej na odpowiednich elementach `<tr>` tabeli klasyfikacji
 - `"positions"` - tablica liczb naturalnych określających pozycje tabeli, do których klasa CSS jest dodawana
 - `"caption"` - opcjonalny opis wyświetlany w legendzie pod klasyfikacją końcową


Ustawienia drabinki
-------------------

Sekcja `"phases"` definiuje już samą drabinkę.

Jest to tablica obiektów - każdy obiekt to kolejna faza (kolumna) drabinki.

Faza ma następujące pola:
 - `"title"` - etykieta fazy, wyświetlana u góry jako link do wyników szczegółowych danej fazy
 - `"link"` - w/w link (ale linki do poszczególnych meczów generują się na podstawie informacji pobranych z bazy, dopóki wszystkie turnieje, których mecze wchodzą w skład danej fazy, są wysyłane do jednej ścieżki)
 - opcjonalną tablicę `"dummies"` - liczb naturalnych pozycji (w pionie), w których dodane będą pionowe odstępy, uwzględniane przy rozmieszczaniu meczów fazy
 - tablicę `"matches"`, definiującej mecze w fazie


Ustawienia kozy (co meczy)
--------------------------

Pola obiektu meczu można podzielić na takie, które definiują strukturę drabinki (awanse, spadki, przejścia między fazami itd.) oraz na takie, które definiują źródło danych do wyświetlenia wyniku i obliczenia rezultatu danego meczu.

Definicję struktury drabinki określają pola:
 - `"id"` - identyfikator meczu (liczbowy, musi być unikatowy)
 - `"teams"` - jest to tablica dwóch elementów, które mogą być:
   + łańcuchem tekstowym - wówczas musi to być pełna nazwa teamu
   + obiektem, z możliwymi polami tablicowymi `"place"`, `"winner"` lub `"loser"` - oznacza to, że dane miejsce drabinki jest przeznaczone dla drużyny z odpowiedniego miejsca z listy teamów (sekcja `"teams"`) lub dla zwycięzców/przegranych w meczach o ID podanych w polu
  Tablica ta jest używana do wyświetlenia możliwych w meczu drużyn, jeśli dane meczu nie mogą być pobrane z innego źródła (np. bazy danych).
 - opcjonalne pola `"winner"` i `"loser"` - które z kolei w tym kontekście oznaczają, miejsca, które zajmują zwycięzcy/przegrani danego meczu w końcowej klasyfikacji
 - opcjonalne pole `"link"` - określające link do wyników meczu, nadpisujący link generowany z bazy turnieju lub linku fazy
 - opcjonalna tablica `"selected_teams"` - jeśli w meczu znana jest już drużyna, ale nie wynika ona ze schematu drabinki (tj. schemat przewidywał wiele możliwości dla danego meczu), można określić znaną/wybraną drużynę, zanim dostępne będą inne źródła danych (baza/HTML) - jest to dwuelementowa tablica liczb całkowitych, określających, które drużyny spośród wszystkich możliwych zostały wybrane (`-1` oznacza brak wyboru, drużyny numerowane są od `0`); drużyny są numerowane w kolejności: `"winner"`, `"loser"`, `"place"`

Dane meczu mogą pochodzić z następujących źródeł:
 - bazy danych turnieju: wówczas należy zdefiniować pola `"database"`, `"round"` i `"table"`
 - strony HTML meczu (tj. strony `PREFIXrundaN.html` dla JFR Teamy lub strony wyników konkretnej rundy dla Tournament Calculatora): wówczas należy zdefiniować pola `"link"` (dla całej fazy lub dla pojedynczego meczu) oraz `"table"`
   + pole `"table"` to widoczny na stronie wyników rundy w pierwszej kolumnie numer stołu
 - ręcznie wpisanego wyniku, wówczas:
   + pole `"score"` określa wynik meczu: może być tablicą dwóch liczb (wynik gospodarzy, wynik gości), może również być słownikiem indeksowanym pełną nazwą teamu lub łańcuchem tekstowym określającym miejsce w tablicy z sekcji `"teams"`
   + opcjonalne pole `"running"` określa, że nie jest zakończony i podaje liczbę rozegranych rozdań (0 dla meczu w przyszłości, >0 dla meczu w trakcie)

Jeżeli wynik zdefiniowany jest w pliku konfiguracyjnym, nie jest pobierany z żadnego innego źródła. Jeśli plik definiuje do tego uczestniczące w meczu teamy, one również nie są pobierane z innych źródeł (ale gdy zdefiniowany jest tylko wynik, teamy wyznaczane są z bazy danych lub danych struktury drabinki).

Wynik ze strony HTML wyników turnieju pobierany jest, jeśli nie uda się pobrać wyniku z bazy danych. Jeśli nie da sięgo pobrać ze stron WWW, program wraca do wypełniania uczestników meczu na podstawie ustawień drabinki.

Na przykładach, pierwszy i ostatni mecz z poniższego pliku:

```
{
  "id": 1,
  "database": "iiild_po_1",
  "round": 1,
  "table": 1,
  "teams": [
    "CKM Łódź",
    "MKS Bzura I Ozorków"
  ],
  "loser": [7, 8]
}
```

Mecz nr 1, pobierany z turnieju `iiild_po_1`, ze stołu nr 1 w pierwszej rundzie.

Gdyby turniej nie był gotowy i rozstawiony, i tak wiadomo, że w meczu gra CKM z Bzurą.

W końcu, przegrany tego meczu zajmie jedno z miejsc 7-8.
Tu uwaga: jeśli okaże się, że żaden inny mecz nie ma dokładnie tego samego warunku - miejsc 7-8 - klasyfikacja prawdopodobnie nie wypełni się, tj. nie można określić, że przegrany jednego meczu zajmie miejsca 7-8, drugiego 8-9, a trzeciego 9-10 i liczyć, że program sam rozwiąże zagadkę.
Nie jest również obsługiwana sytuacja, w której po rozstrzygnięciu jednego z meczów wiadomo już, że wygrany/przegrany zajmie konkretne miejsce w tabeli (bo np. obie drużyny z drugiego meczu "do pary" były niż w klasyfikacji), program zawsze czeka z wypełnieniem klasyfikacji na komplet rozstrzygnięć dotyczących konkretnych miejsc.

```
{
  "id": 14,
  "database": "iiild_po_4",
  "round": 1,
  "table": 2,
  "teams": [
    { "loser": [11, 12] },
    { "loser": [11, 12] }
  ],
  "winner": [15],
  "loser": [16]
}
```

Mecz nr 14 to mecz z drugiego stołu pierwszej rundy turnieju `iiild_po_4`.

Miejsca w tym meczu zajmują przegrani meczów o ID 11 i 12 (przy czym gospodarze/goście są nieznani dopóki turniej nie zostanie rozstawiony w bazie).

Zwycięzca zajmie 15. miejsce w lidze, a przegrany - 16.


Ustawienia swissów
------------------

W sekcji `"swiss"` można zdefiniować pobieranie pozycji drużyn w klasyfikacji końcowej z klasyfikacji wybranych (zakończonych) turniejów JFR Teamy - z ich bazy danych lub strony z wynikami.

Sekcja jest tablicą obiektów określonych przy pomocy następujących właściwości:

 - `"database"`: nazwa bazy danych turnieju źródłowego ALBO
 - `"link"`: URL strony z wynikami (`PREFIXleaderb.html` dla JFR Teamy lub `index.html` dla TournamentCalculatora) swissa
 - `"position"`: pozycja klasyfikacji końcowej, od której wypełniane są miejsca, kolejnymi teamami z klasyfikacji turnieju źródłowego
 - `"position_to"`: opcjonalnie - ostatnia pozycja klasyfikacji końcowej, która ma zostać wypełniona teamami ze swissa (domyślnie - program wypełnia kolejne miejsca, dopóki ma teamy lub miejsca w tabeli)
 - `"swiss_position"`: opcjonalnie - pozycja klasyfikacji swissa, od której program ma rozpocząć pobieranie teamów (domyślnie: od początku tabeli)
 - `"relative_path"`: opcjonalnie - względna ścieżka katalogu WWW turnieju źródłowego (względem katalogu, do którego generowana jest wizualizacja play-off), na potrzeby linku do wyników turnieju
 - `"label"`: opcjonalnie - tekst wyświetlany jako link do swissa nad tabelą klasyfikacji końcowej (domyślnie: `Turniej o []. miejsce`)

Każdy tak zdefiniowany turniej musi być w całości zakończony, a pełne nazwy teamów w nim uczestniczących muszą być zgodne ze zdefiniowanymi w sekcji `teams`.

UWAGA: program nie rozstryga remisów w VP. Teamy o równej liczbie VP klasyfikowane są według kolejności, w jakiej są zdefiniowane w sekcji `teams`.
