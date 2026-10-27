# Strona z publikacjami – instrukcja

## Struktura
- `config.json` – dane osobowe, adres strony (`base_url`), ORCID, linki profili.
- `data/build_data.py` – lista prac (jedno miejsce prawdy). Po zmianie: `python3 data/build_data.py`.
  Pola do uzupełniania: `abstract`, `keywords` (w `publications.json` lub w skrypcie), przydział do projektów.
- `pdfs/` – tu wrzucasz pliki PDF o nazwie `<id>.pdf` (id z kolumny pierwszej w `build_data.py`).
  Generator doda PDF tylko dla prac, dla których prawo udostępnienia na to pozwala.
- `build.py` – generuje stronę do katalogu `docs/`.

## Uruchomienie
```
python3 data/build_data.py
python3 build.py
```

## Wdrożenie na GitHub Pages
1. Utwórz repozytorium `USERNAME.github.io` (adres strony: https://USERNAME.github.io).
2. W `config.json` ustaw `base_url` na ten adres (bez ukośnika na końcu), uzupełnij ORCID.
3. Uruchom `build.py` i wgraj do repozytorium wszystkie pliki z katalogu `docs/` (bez samego folderu; strona jest płaska, bez podfolderów).
4. Settings → Pages → Source: branch `main`, folder `/ (root)`.
5. Google Search Console: dodaj stronę, zgłoś `sitemap.xml`. Bing Webmaster Tools: to samo.
6. Google Scholar indeksuje strony prac sam (znaczniki `citation_*`); zwykle trwa to kilka tygodni.

## Co zawiera strona pod kątem widoczności
- osobna strona dla każdej pracy z meta tagami Highwire (`citation_title`, `citation_author`, `citation_pdf_url`, `citation_doi`) – standard Google Scholar,
- dane strukturalne schema.org (JSON-LD): `Person`, `ScholarlyArticle`, `ResearchProject`, `Grant`,
- `sitemap.xml`, `robots.txt` (wpuszcza też roboty AI: GPTBot, ClaudeBot, PerplexityBot, Google-Extended),
- `llms.txt` – zwięzły opis i lista prac w formacie czytelnym dla modeli językowych,
- `publications.bib` – BibTeX wszystkich prac,
- strony pakietów projektowych z listą prac i numerem grantu.

## Noty przy AAM
Generator wstawia na stronie pracy notę wymaganą przez wydawcę. Tę samą notę umieść na pierwszej stronie pliku PDF z AAM (Elsevier: licencja CC BY-NC-ND 4.0 + DOI; Springer: „Version of Record available at…”; T&F: „Accepted Manuscript of an article published by Taylor & Francis…”).
