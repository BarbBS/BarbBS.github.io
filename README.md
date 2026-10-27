# Strona z publikacjami – jak ją edytować

Strona https://barbbs.github.io buduje się sama. Po każdej zmianie zapisanej w tym repozytorium GitHub uruchamia `build.py` i w 1–2 minuty publikuje nową wersję (zakładka **Actions** → zielony ptaszek).

Edytujesz tylko trzy rodzaje plików. `build.py` i `.github/workflows/build.yml` zostaw bez zmian.

| Plik | Co zawiera |
| --- | --- |
| `profile.md` | opis Twojej osoby, stanowisko, linki, zainteresowania |
| `project-*.md` | jeden plik = jeden projekt (pakiet projektowy) |
| `pub-*.md` | jeden plik = jedna publikacja |
| `<id>.pdf` | pełny tekst pracy (AAM lub PDF wydawcy) |

## Jak edytować plik w przeglądarce

1. Kliknij plik, potem ikonę ołówka (**Edit this file**).
2. Zmień tekst.
3. **Commit changes…** → **Commit changes**.

Budowa każdego pliku `.md` jest taka sama: między dwiema liniami `---` stoją pola `nazwa: wartość`, a pod nimi zwykły tekst (opis lub abstrakt). Akapity oddzielasz pustą linią. Kilka wartości w jednym polu oddzielasz średnikiem.

## Opis osoby – `profile.md`

Pola na górze: stanowisko (`job_title`), afiliacja, linki, `interests` (rozdzielone `;`). Pod drugą linią `---` jest opis; pierwszy akapit trafia też do opisu strony w Google i do `llms.txt`, więc powinien sam w sobie mówić, kim jesteś.

## Nowa publikacja

1. Otwórz `pub-_TEMPLATE.md` i skopiuj jego treść.
2. **Add file → Create new file**. Nazwij plik `pub-<id>.md`, np. `pub-irfa2027-merge.md`. `<id>` to krótka nazwa bez spacji i polskich znaków; staje się adresem strony pracy (`barbbs.github.io/irfa2027-merge.html`).
3. Wklej szablon i uzupełnij pola:

| Pole | Wartości |
| --- | --- |
| `title` | tytuł |
| `authors` | `Nazwisko, I., Nazwisko, I.` – w kolejności z artykułu |
| `year` | rok (liczba) |
| `type` | `article`, `chapter`, `proceedings`, `book`, `wp` (working paper), `report` |
| `venue` | czasopismo / książka / seria |
| `volume_pages` | np. `97, 103809` |
| `doi` | sam DOI, np. `10.1016/j.irfa.2024.103809` |
| `version` | `published` (PDF wydawcy, tylko artykuły OA), `accepted` (AAM), `preprint` (working paper), `none` (bez pełnego tekstu) |
| `license` | tylko dla OA, np. `CC BY 4.0` |
| `projects` | kody projektów rozdzielone `;`, np. `OPUS21; COST` – kod to pole `code` z pliku `project-*.md` |
| `preprint` | link do SSRN itp. (opcjonalnie) |
| `keywords` | słowa kluczowe rozdzielone `;` |

4. Pod drugą linią `---` wklej abstrakt.
5. **Commit changes**.

Working paper, który ukazał się w czasopiśmie: zmień w jego pliku `type`, `venue`, `doi` i `version`; nazwy pliku nie zmieniaj, żeby adres strony został ten sam.

## PDF

**Add file → Upload files**, nazwa pliku = `<id>.pdf` (np. `irfa2027-merge.pdf`). PDF pojawi się na stronie tylko gdy `version` w pliku pracy to `published`, `accepted` albo `preprint`. Przy `accepted` strona sama dodaje notę wymaganą przez wydawcę (Elsevier, Springer, Taylor & Francis – rozpoznawane po DOI). Tę samą notę umieść na pierwszej stronie PDF.

Zasady: Elsevier – AAM od razu, licencja CC BY-NC-ND; Springer/Palgrave – AAM od razu (rozdziały po 12 mies.); Taylor & Francis – AAM po publikacji; PDF wydawcy tylko przy otwartym dostępie.

## Projekt

Plik `project-<kod>.md`: `code` (krótki kod używany w publikacjach), `order` (kolejność na stronie), `name`, `number`, `funder`, `title`, `years`; pod `---` opcjonalny opis projektu. Nowy projekt: skopiuj istniejący plik i zmień pola.

## Gdy coś pójdzie nie tak

Jeśli w **Actions** pojawi się czerwony krzyżyk, kliknij go, potem **build** → krok **Build site**. Komunikat zaczyna się od `BŁĄD w pliku …` i mówi, co poprawić (np. rok nie jest liczbą, nieznany kod projektu). Do czasu poprawki działa poprzednia wersja strony. Każdą zmianę można cofnąć w historii pliku (**History**).
