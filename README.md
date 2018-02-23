JFR Teamy - play-off
====================

Generator drabinek wizualizacji play-off dla turniejów prowadzonych przy użyciu JFR Teamy.

Przykład wizualizacji: [III liga LD, sezon 2016/17](https://emkael.github.io/playoff/).

Wymagania systemowe
-------------------

Dla wersji skompilowanej: jakiś współczesny system rodziny MS Windows.

Dla wersji skryptowej:
 * Python 2.7.x, co najmniej 2.7.9, ze standardowym zestawem bibliotek
 * MySQL connector dla Pythona (opcjonalnie, w przypadku użycia bazy danych jako źródła wyników)
 * `pip install -r requirements.txt`

Instalacja
----------

Dla wersji skompilowanej: [ściągnąć](https://github.com/emkael/jfrteamy-playoff/releases), rozpakować, upewnić się, że [`playoff.js`](playoff.js) jest w katalogu pliku wykonywalnego.

Dla wersji skryptowej: sklonować to repozytorium.

Użycie
------

Niezależnie od wersji, należy wykonać w linii poleceń polecenie:

```
playoff.exe PLIK_USTAWIEŃ_JSON
```

lub

```
python playoff.py PLIK_USTAWIEŃ_JSON
```

`PLIK_USTAWIEŃ_JSON` jest plikiem konfiguracyjnym, dostarczającym wszelkich danych niezbędnych do pracy programu.

Jeśli w wywołaniu nie podano ścieżki do pliku ustawień, program spyta o nią sam.

Jego strukturę opisuje dokument [CONFIG](CONFIG.md).

Znane ograniczenia
------------------

 *  wszystkie mecze danej fazy muszą lądować na FTP w tej samej ścieżce:
linki generowane są na podstawie URL całej fazy (linki z datami u góry),
prefiksów turniejów oraz numerów rund
 * fazy powinny być określone raczej chronologicznie (czytaj: nie
testowano, co się stanie, jeśli określimy np., że w meczu fazy 2 ma zagrać
zwycięzca z fazy 4), ale nie powinno być problemu z "przeskakiwaniem"
faz (czyli awansem zwycięzcy z fazy 1 od razu do fazy 3)
 * program wymaga działania Webmastera (wyniki czytane są z takiego
miejsca bazy, do którego pisze Webmaster, a z jakichś powodów nie pisze
Admin przy zamykaniu rundy/segmentu), więc nawet w przypadku grania
"off-line" (Kolektor+statyczne po każdym segmencie), może być potrzeba
przejechania segmentu Webmasterem
 * przez cały czas trwania play-off pełne nazwy teamów (w bazach i te
określone w JSONie) muszą się zgadzać - teamy są rozróżniane po nich właśnie
 * nie ma możliwości skonfigurowania więcej niż jednego połączenia do MySQL

Autor
-----

Michał Klichowicz (mkl)

Licencja
--------

[Uproszczona licencja BSD](LICENSE)

---

`You're slipping slowly from my reach.`
