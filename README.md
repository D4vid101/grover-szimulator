# Grover-szimulátor

Kvantuminformatikai alkalmazások, 2026 ősz · 3. feladat

Szélyes Dávid és [tamas722](https://github.com/tamas722)

A program a Grover-algoritmus egyetlen megjelölt állapotra vonatkozó esetét mutatja be. Ugyanazt az állapotot látjuk az előjeles amplitúdódiagramon és a geometriai ábrán. Egy kattintással külön követhető az orákulum és a diffúzió.

## Futtatás

- Windows x64: a [Releases](../../releases) oldalról töltsd le a `GroverSzimulator.exe` fájlt, majd indítsd el. Python és internet nem szükséges a futtatáshoz.
- Forrásból: Python 3.10+ és Tk szükséges. A projekt gyökérmappájában futtasd: `python app.py`.
- Windows csomag újraépítése Python 3.12-vel: `python -m pip install PyInstaller==6.22.3`, majd `python -m PyInstaller --onefile --windowed --name GroverSzimulator app.py`. A fájl a `dist` mappába kerül.

## Első próba

Az alapbeállítás két qubitet, a 2-es célindexet és egy iterációt használ. Nyomd meg kétszer a **Következő** gombot. Először a cél amplitúdója +0,5-ről −0,5-re vált, a cél mérési valószínűsége 25% marad. A második lépésben a cél amplitúdója +1 lesz, a többié 0, így a cél mérési valószínűsége 100%. Az **Előző** gombbal visszanézhető bármely lépés.

A részletes használat, a számítás és az ellenőrzés leírása a [dokumentációban](docs/Grover-dokumentacio.pdf) található. A matematikai háttér forrása [Grover eredeti cikke](https://doi.org/10.1103/PhysRevLett.79.325). A tavalyi, megosztott megoldást a felület és a feladat értelmezéséhez néztük át. A Python-kód önálló implementáció. A megvalósításhoz és a dokumentációhoz AI-asszisztenst használtunk.
