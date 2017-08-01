JFR Teamy - play-off - plik konfiguracyjny
==========================================

Przykładowy kompletny plik konfiguracyjny umieszczono w całości u dołu tego pliku.

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
   + `"logoh"` - nagłówek, jak w tabeli admin bazy turnieju
   + `"refresh"` - parametr odświeżania strony drabinki: `0` = wyłączone, liczba naturalna = interwał odświeżania, w sekundach
   + `"width"` i `"height"` - wymiary (w pikselach) miejsca rezerwowanego dla każdego meczu w widoku drabinki (`"width"` bezpośrednio wpływa na rozmieszczanie kolumn, wewnątrz każdej z kolumn mecze rozmieszczane są równomiernie, w zależnie od ich liczby)
   + `"margin"` - odstęp między w/w miejscem (minimalny - jak widać, w przypadku mniejszej liczby meczów w fazie, odstępy się dopasują)
 - sekcji `"canvas"`: ustawień rysowania linii
   + `"winner_h_offset"`, `"winner_v_offset"` - marginesy (poziomy i pionowy) rysowania linii zwycięzców (odpowiednio: pionowych i poziomych, względem środka obszaru)
   + `"loser_h_offset"`, `"loser_v_offset"` - analogiczne marginesy rysowania linii przegranych
   + `"winner_colour"`, `"loser_colour"` - kolory linii zwycięzców i przegranych
 - sekcji `"database"`, zawierającej ustawienia połączenia bazy danych
 - sekcji `"goniec"`, zawierającej ustawienia Gońca (`"enabled"` przyjmuje wartości `0`/`1`)

Ustawienia teamów
-----------------

Dalej mamy sekcję `"teams"`, która jest pierwsza do przebudowy (albo do odstrzału, w ogóle), więc zbytnio nie przyzwyczajałbym się do jej struktury.

W niej definiujemy teamy w kolejności, wg której mają być rozdzielane miejsca (w sytuacjach "przegrani zajmują miejsca...").

Każdy team to tablica, kolejno: pełnej nazwy (tej, która MUSI się zgadzać z nazwami we wszystkich turniejach), skróconej nazwy, pliku flagi (opcjonalnie).

Jako czwarty element każdej tablicy można wpisać liczbę naturalną, która oznacza pozycję, jaką team ma zająć w końcowej klasyfikacji (tj. wpisanie tam liczby oznacza, że team od samego początku umieszczany jest na tej pozycji w klasyfikacji końcowej - np. jeśli nie uczestniczy w ogóle w play-off).

Co zrobić, gdy jest taki team, a turniej nie ma ustawionych obrazków z flagami? Ustawić flagę na `null` - nie zostanie wyświetlona.

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

Mecz ma następujące pola:
 - `"id"` - identyfikator meczu (liczbowy, musi być unikatowy)
 - `"database"`, `"round"` i `"table"` - określają, skąd brać dane meczu
 - `"teams"` określa, co ma się wyświetlić w przypadku, gdy z powyższego
zestawu pól nie da się pobrać informacji o meczu
  Jest to tablica dwóch elementów, które mogą być:
   + łańcuchem tekstowym - wówczas musi to być pełna nazwa teamu
   + obiektem, z możliwymi polami tablicowymi `"place"`, `"winner"` lub `"loser"` - oznacza to, że dane miejsce drabinki jest przeznaczone dla drużyny z odpowiedniego miejsca z listy teamów (sekcja `"teams"`) lub dla zwycięzców/przegranych w meczach o ID podanych w polu
 - opcjonalne, pola `"winner"` i `"loser"` - które z kolei w tym kontekście oznaczają, miejsca, które zajmują zwycięzcy/przegrani danego meczu w końcowej klasyfikacji

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

Pełen plik konfiguracyjny
-------------------------

```
{
    "output": "D:/Brydz/Teamy/www/liga_playoff_12.html",
    "page": {
        "title": "III liga 2016/17, WZBS Łódź, play-off",
        "logoh": "<span id=\"logo\"></span><script type=\"text/javascript\">loadIt('liga_logo.html','logo');</script>",
        "refresh": 0,
        "width": 200,
        "height": 80,
        "margin": 70
    },
    "canvas": {
        "winner_h_offset": 8,
        "loser_h_offset": 14,
        "winner_v_offset": -6,
        "loser_v_offset": 6,
        "loser_colour": "#ff0000",
        "winner_colour": "#00ff00"
    },
    "database": {
        "host": "localhost",
        "port": 3306,
        "user": "UŻYTKOWNIK BAZY",
        "pass": "HASŁO BAZY"
    },
    "goniec": {
        "enabled": 1,
        "host": "localhost",
        "port": 8090
    },
    "teams": [
        ["Mazowia Płock", "Mazowia", "herby/wp.png"],
        ["Jagielloński Ośrodek Kultury Łódź", "JOK", "herby/el.png"],
        ["KDK II Kutno", "KDK II", "herby/eku.png"],
        ["BINŻ Bełchatów", "BINŻ", "herby/ebe.png"],
        ["CKM Łódź", "CKM", "herby/el.png"],
        ["PTC - PAFANA I Pabianice", "PTC", "herby/epa.png"],
        ["Intra Łódź", "Intra", "herby/el.png"],
        ["BOK Rondo Łódź", "Rondo", "herby/el.png"],
        ["MKS Bzura I Ozorków", "Bzura", "herby/ezgozo.png"],
        ["Zdrowie Piast Sieradz", "Piast", "herby/esi.png"],
        ["Olimpia Chąśno", "Olimpia", "herby/elc.png"],
        ["Brydż Quartet Lechia Tomaszów Mazowiecki", "Lechia", "herby/etm.png"],
        ["Veolia Energia Łódź", "Veolia", "herby/el.png"],
        ["Ekolog Łódź", "Ekolog", "herby/el.png"],
        ["KDK III Kutno", "KDK III", "herby/eku.png"],
        ["Pomiar - Ceemka Opoczno", "Ceemka", "herby/eop.png"]
    ],
    "phases": [
        {
            "title": "25.02.2017",
            "link": "http://arturwasiak.republika.pl/brydz/sedzia/3liga_2016_17/faza_3/liga_runda1.html",
            "matches": [
                {
                    "id": 1,
                    "database": "iiild_po_1",
                    "round": 1,
                    "table": 1,
                    "teams": [
                        { "place": [5] },
                        { "place": [7, 8] }
                    ],
                    "loser": [7, 8]
                },
                {
                    "id": 2,
                    "database": "iiild_po_1",
                    "round": 1,
                    "table": 2,
                    "teams": [
                        { "place": [6] },
                        { "place": [7, 8] }
                    ],
                    "loser": [7, 8]
                },
                {
                    "id": 3,
                    "database": "iiild_po_1",
                    "round": 1,
                    "table": 3,
                    "teams": [
                        { "place": [9] },
                        { "place": [11, 12] }
                    ],
                    "winner": [9, 10]
                },
                {
                    "id": 4,
                    "database": "iiild_po_1",
                    "round": 1,
                    "table": 4,
                    "teams": [
                        { "place": [10] },
                        { "place": [11, 12] }
                    ],
                    "winner": [9, 10]
                }
            ]
        },
        {
            "title": "26.02.2017",
            "link": "http://arturwasiak.republika.pl/brydz/sedzia/3liga_2016_17/faza_4/liga_runda1.html",
            "matches": [
                {
                    "id": 5,
                    "database": "iiild_po_2",
                    "round": 1,
                    "table": 1,
                    "teams": [
                        "BINŻ Bełchatów",
                        { "winner": [1, 2] }
                    ],
                    "loser": [5, 6]
                },
                {
                    "id": 6,
                    "database": "iiild_po_2",
                    "round": 1,
                    "table": 2,
                    "teams": [
                        "KDK II Kutno",
                        { "winner": [1, 2] }
                    ],
                    "loser": [5, 6]
                },
                {
                    "id": 7,
                    "database": "iiild_po_2",
                    "round": 1,
                    "table": 3,
                    "teams": [
                        "Pomiar - Ceemka Opoczno",
                        { "loser": [3, 4] }
                    ],
                    "winner": [11, 12]
                },
                {
                    "id": 8,
                    "database": "iiild_po_2",
                    "round": 1,
                    "table": 4,
                    "teams": [
                        "Olimpia Chąśno",
                        { "loser": [3, 4] }
                    ],
                    "winner": [11, 12]
                }
            ]
        },
        {
            "title": "08.04.2017",
            "link": "http://arturwasiak.republika.pl/brydz/sedzia/3liga_2016_17/faza_5/liga_runda1.html",
            "matches": [
                {
                    "id": 9,
                    "database": "iiild_po_3",
                    "round": 1,
                    "table": 1,
                    "teams": [
                        "Mazowia Płock",
                        { "winner": [5, 6] }
                    ],
                    "loser": [3, 4]
                },
                {
                    "id": 10,
                    "database": "iiild_po_3",
                    "round": 1,
                    "table": 2,
                    "teams": [
                        "Jagielloński Ośrodek Kultury Łódź",
                        { "winner": [5, 6] }
                    ],
                    "loser": [3, 4]
                },
                {
                    "id": 11,
                    "database": "iiild_po_3",
                    "round": 1,
                    "table": 3,
                    "teams": [
                        "Veolia Energia Łódź",
                        { "loser": [7, 8] }
                    ],
                    "winner": [13, 14]
                },
                {
                    "id": 12,
                    "database": "iiild_po_3",
                    "round": 1,
                    "table": 4,
                    "teams": [
                        "Brydż Quartet Lechia Tomaszów Mazowiecki",
                        { "loser": [7, 8] }
                    ],
                    "winner": [13, 14]
                }
            ]
        },
        {
            "title": "09.04.2017",
            "link": "http://arturwasiak.republika.pl/brydz/sedzia/3liga_2016_17/faza_6/liga_runda1.html",
            "matches": [
                {
                    "id": 13,
                    "database": "iiild_po_4",
                    "round": 1,
                    "table": 1,
                    "teams": [
                        { "winner": [9, 10] },
                        { "winner": [9, 10] }

                    ],
                    "winner": [1],
                    "loser": [2]
                },
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
            ]
        }
    ]
}
```
