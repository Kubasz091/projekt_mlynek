# Projekt_Młynek

## Dane autora
- Imie: Jakub
- Nazwisko: Szuzbda
- Wydział: Eiti, PW

## Cel i Opis Projektu
- Cel: 
    Napisać program grający w Młynek. Powinna być możliwość rozgrywki na planszy wynikającej z wybranej na początku liczby pionków (kształt planszy wynika z tej liczby, ale nie reguły gry - można próbować znaleźć taki opis planszy, żeby kod do gry był wspólny).

    Powinna być możliwość gry:
    - dwóch osób ze sobą,
    - osoby z komputerem.

    Program powinien kontrolować poprawność wykonywanych ruchów. Interfejs z użytkownikiem może być tekstowy.

    Algorytm gry przez komputer powinien mieć dwa tryby:
    - komputer wykonuje losowy ruch spośród dostępnych,
    - komputer na bazie prostych reguł wybiera "najlepszy" ruch.

- Opis: 
    W moim projekcie zostały zrealizowane wymienione powyżej w rzeczy. Jest możliwość gry na planszy wynikającej z wybranej na początku ilości pionków, reguły gry nie wynikają z rozmiaru planszy. Jest możliwość gry dwóch osób ze sobą, albo z botem, zależnie którą opcję wybierze się na początku działania programu. Zrobiłem graficzny interfejs bazujący na bibliotece curses znajdującej się domyślnie w pythonie na linuxie. Jej używam do wyświetlania planszy, jak i wszytskich wizualnych informacji. Dane potrzebne do budowy plansz podzieliłem na graficzne zbudwane z znaków (alt keys) i pozycyjne. Zanajdują się w pliku graphic_data.py. Program kontroluje poprawność ruchów, w taki sposób, że nie pozwala wykonać ruchu który jest nie poprawny, jeżeli spróbujemy odstawić pionek na pole, albo w miejscu w którym nie powinien się znaleźć wróci na swoje poprzednie miejsce. Interfejs z użytkownikiem jest graficzny, lecz również w terminalu, sterowanie przebiega w następujący sposób: 
    - q - zakończenie programu, 
    - e - próba podniesienia pionka (lub usunięcia), 
    - strzałki - poruszanie się po ekranie kursorem.

    Bot ma dwa tryby, które wybierane są, jeśli wybierzemy, że chcemy grać z botem: randomowy, oraz kierowany prostymi zasadami:

    Przy ruchu normalnym:
    - sprawdza, czy jest w stanie ułożyć młynek,
    - jeśli nie, to czy jest w stanie zablokować młynek, który najprawdopodobniej zostanie ułożony przez przeciwnika,
    - jeśli nie to wykonuje losowy ruch z puli możliwych, usuwając uprzednio, jeżeli to nie usunie wszystkiech ruchów te które niszczyłyby jego młynki, albo umożliwiały zrobienie młynka przciwnikowi w następnym ruchu.

    Przy ruchu usuwającym:
    - spradza, czy przeciwnik ma 2 pionki które w następnym ruchu mogą zostać ułożone w młynek, jeśli tak to usuwa losowy z nich,
    - jeśli nie to sprawdza czy któryś z potencjalnych młynków bota jest blokowany, przez pionek gracza jeśli tak to go usuwa,
    - jeśli nic nie znajdzie to usuwa losowy pionek nie znajdujący się obecjnie w młynku, chyba że wszystkie się znajdują to wtedy losowy.

## Struktura Klas
- Pawn: każdy pionek jest typu Pawn, ma pozycje i przynależność do danego z graczy, przechowuje również pionki z którymi jest w młynku, jeżeli jest i pole na którym się znajduje, jeżeli już został ruszony.
- Dot: przechowuje stoją pozycje na planczy, oraz z którymi polami jest połączona, licząc od lewego górnego rogu, od lewej do prawej, wiersz pól po wierszu oraz czy ma jakiś pionek na sobie.
- Bot: znajduje się w tej klasie logika zachowań bota, albo jej brak w przypadku ruchów losowych :D. 
- Display: klasa ta zajmuje się wyświetlaniem planszy, pionków, itd. w terminalu za pomocą biblioteki curses.
- GameLord: jest to klasa w której znajdują się metody prawie wszystkiego co się dzieje w grze niezwiązanego z wyświetlaniem, czy pamiętaniem ruchów.
- GraphicData: jest to klasa która zawiera całą grafikę w grze poza napisami i kursorem, została przezemnie stworzona w celu napisania w niej danych potrzebnych do budowy planszy, i logiki na niej, jako że nie była to jakaś ogromna ilość danych, oraz potrzbny był mi łatwy dostęp do danych w celu ich zmiany, kiedy coś nie działało nie robiłem tego w pliku json.
- ProgramRunner: rusza program, celem jego stowrzenia, było zapamietanie i przekazanie danych wprowadzonych przez użytkownika na starcie dalej, tak aby dało się to zgrać z biblioteką curses.
- PawnPlacementSaver: klasa ta zapisuje położenia pionków na planczy jako listę 0, 1 i 2 odpowiednio 0 - brak pionka na polu, 1 - pionek gracza 1, 2 - pionek gracza 2, oraz od ilu ruchów nie został ułożony młynek w skrócie sprawdza czy nie doszło do remisu.

## Przewodnik Użytkownika
- Krok 1: sklonować repozytorium.
- Krok 2: upewnić się, że zostało ono otworzone na maszynie wirtualnej, lub systemie linux.
- Krok 3: otworzyć plik main.py oraz go uruchomić.

## Refleksja
- Wykorzystane Prace: przykłady wykorzystania biblioteki curses, tablica altkeys z strony: [AltKody](https://fsymbols.com/pl/klawiatura/windows/alt-kody/lista/) oraz edytor grafik altkodes: [Fsymbols](https://fsymbols.com/draw/).
- Niespełnione Cele: zrobienie drugiego sposobu sterowania, który "skakałby" od możliwości do możliwości, odkrycie jakiegoś sposobu na generowanie plansz, bez potrzeby zapisywania ich danych, na podstawie jakiś zasad, któych nie udało mi się odkryć.
- Napotkane Przeszkody: ułożenie planszy, i zrobienie logiki gry.
- Zmiany w Porównaniu do Planowanego Rozwiązania: na początku chciałem zrobić generowanie plansz na podstawie jakiegoś wzoru, ale nie udało mi się nic wymyślić, więc zapisałem je ręcznie, ragment po fragmencie.
