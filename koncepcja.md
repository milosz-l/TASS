# Analiza sieci społecznościowych
## Projekt 2

### Koncepcja wykonania

**Skład zespołu:**

-   Marcel Tracz
-   Łopatto Miłosz
-   Włodarz Jakub

**Temat projektu:**

Pogrupuj leki refundowane według substancji czynnych. Sprawdź, jaki udział w poszczególnych grupach mają podmioty odpowiedzialne, na podstawie kwot refundacji.

**Źródła danych:**

-   [Rejestr Produktów Leczniczych](https://rejestry.ezdrowie.gov.pl/registry/rpl) - zawiera informacje o wszystkich produktach leczniczych przeznaczonych dla ludzi oraz weterynaryjnych dopuszczonych do obrotu na terytorium Rzeczypospolitej Polskiej.
-   [Obwieszczenia Ministra Zdrowia dotyczące leków refundowanych](https://archiwum.mz.gov.pl/leki/refundacja/lista-lekow-refundowanych-obwieszczenia-ministra-zdrowia/)
-   [Obwieszczenia refundacyjne publikowane przez Ministerstwo Zdrowia](https://ezdrowie.gov.pl/portal/home/dla-podmiotow-leczniczych/narzedzie-pomagajace-okreslic-poziom-refundacji)

Powyższe źródła zawierają aktualne informacje o produktach leczniczych i zasadach refundacji w Polsce. Są to gotowe zbiory danych. Kluczem łączącym te zbiory będzie kod EAN. Wszystkie opakowania handlowe produktów leczniczych (poza lekami wydawanymi na receptę) dostępnych na rynku polskim są znakowane kodem EAN-13. W kodzie tym przedstawiony jest numer identyfikacyjny leku, tj. numer GTIN.

**Wybrane technologie:**

-   **MongoDB**
    -   Rola: Baza danych NoSQL do przechowywania i przetwarzania danych w formacie JSON.
    -   Dlaczego: Skalowalność, łatwa integracja z aplikacjami webowymi, możliwość replikacji.
-   **NetworkX**
    -   Rola: Analiza grafów grupujących leki według substancji czynnych i podmiotów odpowiedzialnych.
    -   Dlaczego: Pozwala modelować dane jako grafy, co ułatwia analizę relacji między substancjami czynnymi a podmiotami.
-   **Streamlit**
    -   Rola: Interfejs użytkownika do wizualizacji danych, analiz i interakcji z użytkownikiem.
    -   Dlaczego: Łatwa integracja z Pythonem, szybkie prototypowanie aplikacji interaktywnych.

**Scenariusz użycia aplikacji przez użytkownika:**

1. Użytkownik otwiera aplikację bez logowania, trafiając na główny interfejs, który umożliwia mu łatwą nawigację po dostępnych funkcjach.
2. Użytkownik wybiera opcję grupowania leków według substancji czynnych, dzięki czemu może przeglądać leki w ułożeniu według ich aktywnych składników.
3. Użytkownik przegląda szczegóły dotyczące podmiotów odpowiedzialnych za leki, analizując ich udziały w refundacjach oraz powiązania tych podmiotów z substancjami czynnymi.
4. Użytkownik eksportuje zebrane informacje do pliku w formacie określonym przez aplikację.

**Ergonomia Aplikacji:**

-   Intuicyjny interfejs: proste menu w Streamlit z wyborem grupowania i analiz.
-   Szybki dostęp: wyniki analizy pojawiają się w czasie rzeczywistym.
-   Responsywność: dostosowanie interfejsu do różnych urządzeń.
-   Eksport danych: prosty przycisk umożliwiający pobranie wyników.
-   Wielodostępność aplikacji.

**Architektura:**

-   Warstwa danych: MongoDB jako centralna baza danych NoSQL.
-   Warstwa analizy: NetworkX do grupowania i analizy grafowej.
-   Warstwa aplikacji i prezentacji (frontend i backend): Streamlit jako interfejs użytkownika z wykresami i tabelami.