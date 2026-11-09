# Grover-szimulátor

A Kvantuminformatikai alkalmazások tantárgy 2026. őszi házi feladatának beadása (3. feladat).

Szélyes Dávid és [tamas722](https://github.com/tamas722)

A program a Grover-algoritmus egyetlen megjelölt állapotra vonatkozó esetét mutatja be. Ugyanazt az állapotot látjuk az előjeles amplitúdódiagramon és a geometriai ábrán. Egy kattintással külön követhető az orákulum és a diffúzió.

## Futtatás

- Windows: töltsd le a [legfrissebb beadási ZIP-et](../../releases/latest), csomagold ki, és nyisd meg a `GroverSzimulator.html` fájlt a böngészőben. A fájl önállóan, internetkapcsolat és telepítés nélkül fut.
- A böngészős változat újraépítése: Python 3.10+ alatt futtasd a `python build_browser.py` parancsot. A program a `grover.py` eredményeit beépíti a `browser-template.html` sablonba.
- Asztali fejlesztői nézet: Python 3.10+ és Tk szükséges. A projekt gyökérmappájában futtasd: `python app.py`.

## Első próba

Az alapbeállítás két qubitet, a 2-es célindexet és egy iterációt használ. Nyomd meg kétszer a **Következő** gombot. Először a cél amplitúdója +0,5-ről −0,5-re vált, a cél mérési valószínűsége 25% marad. A második lépésben a cél amplitúdója +1 lesz, a többié 0, így a cél mérési valószínűsége 100%. Az **Előző** gombbal visszanézhető bármely lépés.

A részletes használat, a számítás és az ellenőrzés leírása a [dokumentációban](docs/Grover-dokumentacio.pdf) található. A matematikai háttér forrása [Grover eredeti cikke](https://doi.org/10.1103/PhysRevLett.79.325). A tavalyi, megosztott megoldást a felület és a feladat értelmezéséhez néztük át. A Python-kód önálló implementáció. A megvalósításhoz és a dokumentációhoz AI-asszisztenst használtunk.
