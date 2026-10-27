#!/usr/bin/env python3
"""Buduje statyczną stronę z publikacjami (GitHub Pages).
Dane: data/publications.json, data/projects.json, config.json.
PDF-y: wrzuć plik do pdfs/<id>.pdf (np. pdfs/frl2024-dirtyclean.pdf) i uruchom ponownie.
Wynik: katalog docs/ (GitHub Pages -> Settings -> Pages -> branch main, folder /docs).
"""
import json, html, re, shutil, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
CFG = json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
PUBS = json.loads((ROOT/"data/publications.json").read_text(encoding="utf-8"))
PROJ = json.loads((ROOT/"data/projects.json").read_text(encoding="utf-8"))
OUT = ROOT/"docs"
BASE = CFG["base_url"].rstrip("/")
TODAY = datetime.date.today().isoformat()
e = lambda s: html.escape(str(s or ""), quote=True)

# Które wersje wolno pokazać publicznie jako pełny tekst
FULLTEXT_OK = {"vor": "Published version (open access)", "vor_check": "Published version (open access)",
               "aam_elsevier": "Accepted manuscript", "aam_springer": "Accepted manuscript",
               "aam_springer_ch": "Accepted manuscript", "aam_tf": "Accepted manuscript",
               "own": "Working paper"}
TYPE_LABEL = {"article": "Journal article", "chapter": "Book chapter", "proceedings": "Conference paper",
              "book": "Book", "wp": "Working paper", "report": "Report"}
SCHEMA_TYPE = {"article": "ScholarlyArticle", "chapter": "Chapter", "proceedings": "ScholarlyArticle",
               "book": "Book", "wp": "ScholarlyArticle", "report": "Report"}

def notice(p):
    """Nota wymagana przez wydawcę przy wersji AAM."""
    doi = f"https://doi.org/{p['doi']}" if p["doi"] else ""
    s = p["share"]
    if s == "aam_elsevier":
        return f"© {p['year']}. This manuscript version is made available under the CC-BY-NC-ND 4.0 license https://creativecommons.org/licenses/by-nc-nd/4.0/. The published article is available at {doi}."
    if s in ("aam_springer", "aam_springer_ch"):
        return f"This is an accepted manuscript version, subject to Springer Nature's AM terms of use. It is not the Version of Record. The Version of Record is available online at {doi}."
    if s == "aam_tf":
        return f"This is an Accepted Manuscript of an article published by Taylor & Francis in {p['venue']} ({p['year']}), available at {doi}."
    return ""

def pdf_path(p):
    f = ROOT/"pdfs"/f"{p['id']}.pdf"
    return f if f.exists() and p["share"] in FULLTEXT_OK else None

def authors_list(p):
    a = re.sub(r"\s+i in\..*$|\(.*?\)", "", p["authors"]).strip().rstrip(",")
    parts = [x.strip() for x in re.split(r",\s*(?=[^,]+,\s*[A-ZŁŚŻŹĆÓ][\w.\-]*\.)", a)]
    return [x for x in parts if x]

def css():
    return """
:root{--bg:#f7f9fc;--fg:#141c2e;--muted:#56617a;--line:#dce3ef;--accent:#1f3a6e;--hover:#3f63c9;--tag:#e6ecf8;--oa:#2b6e46}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0e1526;--fg:#e4eaf6;--muted:#9aa7c2;--line:#25314c;--accent:#93b2f4;--hover:#b9cdfa;--tag:#1a2643;--oa:#79d29f}}
a:hover{color:var(--hover)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 "Source Serif 4",Georgia,serif}
a{color:var(--accent)}.wrap{max-width:1120px;margin:0 auto;padding:40px 16px 0;display:grid;grid-template-columns:230px minmax(0,1fr);gap:48px}
main{min-width:0;max-width:780px}footer{max-width:1120px;margin:0 auto;padding:0 16px}
aside{position:sticky;top:24px;align-self:start;max-height:calc(100vh - 48px);overflow:auto;font:14px/1.45 system-ui,sans-serif}
aside .who{font:600 16px/1.3 "Source Serif 4",Georgia,serif;color:var(--fg);text-decoration:none;display:block;margin-bottom:14px}
aside ul{list-style:none;margin:0;padding:0}aside li{margin:2px 0}aside a{color:var(--fg);text-decoration:none;display:flex;justify-content:space-between;gap:8px;padding:3px 8px;border-radius:4px}
aside a:hover{background:var(--tag);color:var(--hover)}aside .n{color:var(--muted);font-variant-numeric:tabular-nums}aside .grp{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:16px 8px 4px}
aside ul.sub a{padding-left:20px;font-size:13px;color:var(--muted)}aside .ext{margin-top:16px;border-top:1px solid var(--line);padding-top:10px}
h2[id]{scroll-margin-top:16px}
@media (max-width:820px){.wrap{display:block;padding-top:20px}aside{position:static;max-height:none;margin-bottom:24px;border-bottom:1px solid var(--line);padding-bottom:12px}aside ul.sub{display:none}aside ul.toc{display:flex;flex-wrap:wrap;gap:4px}aside .grp{display:none}aside .ext{display:none}}
h1{font-size:2rem;margin:0 0 4px;line-height:1.2}h2{font-size:1.3rem;margin:40px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
h3{font-size:1.05rem;margin:0 0 4px}.muted{color:var(--muted)}
.pub{padding:12px 0;border-bottom:1px solid var(--line)}.pub p{margin:2px 0}.meta{font:14px/1.5 system-ui,sans-serif;color:var(--muted)}
.tag{display:inline-block;font:12px/1.4 system-ui,sans-serif;background:var(--tag);padding:1px 8px;border-radius:10px;margin:4px 6px 0 0;text-decoration:none;color:var(--fg)}
.tag.oa{color:var(--oa)}.box{border:1px solid var(--line);padding:14px 16px;border-radius:6px;margin:16px 0}
footer{margin-top:48px;padding-bottom:40px;font:13px/1.5 system-ui,sans-serif;color:var(--muted)}
ul.plain{padding-left:18px}code{font-size:.85em}"""

def page(title, desc, body, path, head_extra="", jsonld=None):
    SIDEBAR_ = SIDEBAR
    canon = f"{BASE}/{path}"
    verif = f'<meta name="google-site-verification" content="{e(CFG["google_site_verification"])}">' if (CFG.get("google_site_verification") and path == "") else ""
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(canon)}"><meta property="og:type" content="website">
<link rel="alternate" type="text/plain" href="{BASE}/llms.txt" title="LLM-readable summary">
{head_extra}{verif}<link rel="stylesheet" href="{BASE}/style.css">{ld}</head><body>
<div class="wrap"><aside>{SIDEBAR_}</aside>
<main>{body}</main></div>
<footer>{e(CFG['name'])} · {e(CFG['affiliation'])} · Last updated {TODAY}</footer></body></html>"""

def person_ld():
    same = [u for u in [CFG.get("google_scholar"), CFG.get("repec"), CFG.get("university_profile"),
                        f"https://orcid.org/{CFG['orcid']}" if CFG.get("orcid") else ""] if u]
    return {"@type": "Person", "@id": f"{BASE}/#person", "name": CFG["name"], "alternateName": CFG["name_ascii"],
            "jobTitle": CFG["job_title"], "worksFor": {"@type": "CollegeOrUniversity", "name": CFG["affiliation"]},
            "knowsAbout": CFG["interests"], "sameAs": same, "url": f"{BASE}/"}

SECTIONS = [("articles", "Journal articles", ["article"]), ("chapters", "Book chapters and conference papers", ["chapter", "proceedings"]),
            ("books", "Books and reports", ["book", "report"]), ("working-papers", "Working papers and preprints", ["wp"])]
SIDEBAR = ""

def make_sidebar(pubs, by_proj):
    cnt = {sid: sum(1 for p in pubs if p["type"] in ts) for sid, _, ts in SECTIONS}
    short = {"articles": "Journal articles", "chapters": "Chapters & conference papers", "books": "Books & reports", "working-papers": "Working papers"}
    li = lambda href, label, n="": f'<li><a href="{href}"><span>{e(label)}</span><span class="n">{n}</span></a></li>'
    pubs_li = "".join(li(f"{BASE}/#{sid}", short[sid], cnt[sid]) for sid in ("articles", "chapters", "books") if cnt[sid])
    projs = [(k, pr) for k, pr in PROJ.items() if by_proj[k]]
    sub = "".join(li(proj_url(k), pr["name"].replace("NCN ", "NCN ").replace("COST Action CA19130 FinAI", "COST FinAI").replace("MSCA Doctoral Network DIGITAL", "MSCA DIGITAL").replace("Regionalna Inicjatywa Doskonałości (MNiSW)", "RID (MNiSW)"), len(by_proj[k])) for k, pr in projs)
    links = [("Google Scholar", CFG["google_scholar"]), ("ORCID", f"https://orcid.org/{CFG['orcid']}" if CFG["orcid"] else ""), ("RePEc", CFG["repec"]), ("University profile", CFG["university_profile"]), ("BibTeX", f"{BASE}/publications.bib")]
    ext = "".join(li(e(u), n) for n, u in links if u)
    return (f'<a class="who" href="{BASE}/">{e(CFG["name"])}</a><nav aria-label="Contents">'
            f'<p class="grp">Publications</p><ul class="toc">{pubs_li}'
            f'{li(f"{BASE}/#projects", "Research projects", len(projs))}</ul><ul class="sub">{sub}</ul>'
            f'<ul class="toc">{li(f"{BASE}/#working-papers", "Working papers", cnt["working-papers"])}</ul>'
            f'<ul class="ext">{ext}</ul></nav>')

def pub_url(p): return f"{BASE}/{p['id']}.html"
def pdf_url(p): return f"{BASE}/{p['id']}.pdf"
def proj_url(k): return f"{BASE}/project-{k.lower()}.html"

def pub_item(p):
    tags = []
    if pdf_path(p): tags.append(f'<a class="tag oa" href="{pdf_url(p)}">PDF · {FULLTEXT_OK[p["share"]]}</a>')
    if p["doi"]: tags.append(f'<a class="tag" href="https://doi.org/{e(p["doi"])}">DOI</a>')
    if p["ssrn"] and p["ssrn"] != f"https://doi.org/{p['doi']}": tags.append(f'<a class="tag" href="{e(p["ssrn"])}">SSRN preprint</a>')
    for k in p["projects"]: tags.append(f'<a class="tag" href="{proj_url(k)}">{e(PROJ[k]["name"])}</a>')
    vp = f", {p['volpages']}" if p["volpages"] else ""
    return f"""<div class="pub"><h3><a href="{pub_url(p)}">{e(p['title'])}</a></h3>
<p>{e(p['authors'])} ({p['year']}). <em>{e(p['venue'])}</em>{e(vp)}.</p><p>{''.join(tags)}</p></div>"""

def build_pub(p):
    pdf = pdf_path(p)
    if pdf: shutil.copy(pdf, OUT/f"{p['id']}.pdf")
    auths = authors_list(p)
    meta = [f'<meta name="citation_title" content="{e(p["title"])}">']
    meta += [f'<meta name="citation_author" content="{e(a)}">' for a in auths]
    meta.append(f'<meta name="citation_publication_date" content="{p["year"]}">')
    if p["type"] in ("article", "proceedings"): meta.append(f'<meta name="citation_journal_title" content="{e(p["venue"])}">')
    elif p["type"] == "chapter": meta.append(f'<meta name="citation_inbook_title" content="{e(p["venue"])}">')
    elif p["type"] in ("wp", "report"): meta.append(f'<meta name="citation_technical_report_institution" content="{e(p["venue"])}">')
    if p["doi"]: meta.append(f'<meta name="citation_doi" content="{e(p["doi"])}">')
    if pdf: meta.append(f'<meta name="citation_pdf_url" content="{pdf_url(p)}">')
    meta.append(f'<meta name="citation_abstract_html_url" content="{pub_url(p)}">')
    abstract = p.get("abstract") or ""
    desc = abstract[:155] if abstract else f"{p['title']} — {TYPE_LABEL[p['type']].lower()} by {p['authors']}, {p['venue']} ({p['year']})."
    funding = [PROJ[k] for k in p["projects"]]
    ld = {"@context": "https://schema.org", "@type": SCHEMA_TYPE[p["type"]], "@id": pub_url(p), "name": p["title"], "headline": p["title"][:110],
          "author": [{"@type": "Person", "name": a, **({"@id": f"{BASE}/#person"} if "Będowska" in a or "Bedowska" in a else {})} for a in auths],
          "datePublished": str(p["year"]), "url": pub_url(p), "inLanguage": "pl" if re.search(r"[ąęśćżźłń]", p["title"]) else "en",
          "isPartOf": {"@type": "Periodical" if p["type"] == "article" else "CreativeWork", "name": p["venue"]}}
    if p["doi"]: ld["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI", "value": p["doi"]}; ld["sameAs"] = f"https://doi.org/{p['doi']}"
    if abstract: ld["abstract"] = abstract
    if p["keywords"]: ld["keywords"] = p["keywords"]
    if p["license"].startswith("CC"): ld["license"] = p["license"]
    if pdf: ld["encoding"] = {"@type": "MediaObject", "contentUrl": pdf_url(p), "encodingFormat": "application/pdf"}
    if funding: ld["funding"] = [{"@type": "Grant", "identifier": f["number"], "name": f["name"], "funder": {"@type": "Organization", "name": f["funder"]}} for f in funding]
    body = f"""<p class="muted">{TYPE_LABEL[p['type']]} · {p['year']}</p><h1>{e(p['title'])}</h1>
<p>{e(p['authors'])}</p><p><em>{e(p['venue'])}</em>{(', ' + e(p['volpages'])) if p['volpages'] else ''}</p>
{f'<p>DOI: <a href="https://doi.org/{e(p["doi"])}">{e(p["doi"])}</a></p>' if p['doi'] else ''}
{f'<h2>Abstract</h2><p>{e(abstract)}</p>' if abstract else ''}
{f'<p><strong>Keywords:</strong> {e(", ".join(p["keywords"]))}</p>' if p['keywords'] else ''}
<div class="box">{f'<p><a href="{pdf_url(p)}"><strong>Download PDF</strong></a> — {FULLTEXT_OK[p["share"]]}</p>' if pdf else '<p>Full text: see the publisher version via DOI.</p>'}
{f'<p class="meta">{e(notice(p))}</p>' if pdf and notice(p) else ''}
{f'<p class="meta">Preprint: <a href="{e(p["ssrn"])}">{e(p["ssrn"])}</a></p>' if p['ssrn'] else ''}</div>
{('<h2>Funding</h2><ul class="plain">' + ''.join(f'<li><a href="{proj_url(k)}">{e(PROJ[k]["name"])}</a>, {e(PROJ[k]["funder"])}, grant {e(PROJ[k]["number"])}</li>' for k in p['projects']) + '</ul>') if p['projects'] else ''}
<h2>Cite</h2><pre style="white-space:pre-wrap;font-size:13px">{e(bibtex(p))}</pre>"""
    (OUT/f"{p['id']}.html").write_text(page(f"{p['title']} | {CFG['name']}", desc, body, f"{p['id']}.html", "\n".join(meta), ld), encoding="utf-8")

def bibtex(p):
    kind = {"article": "article", "chapter": "incollection", "proceedings": "inproceedings", "book": "book", "wp": "techreport", "report": "techreport"}[p["type"]]
    venue_key = {"article": "journal", "chapter": "booktitle", "proceedings": "booktitle", "book": "publisher", "wp": "institution", "report": "institution"}[p["type"]]
    f = {"title": p["title"], "author": " and ".join(authors_list(p)), "year": p["year"], venue_key: p["venue"]}
    if p["volpages"]: f["note"] = p["volpages"]
    if p["doi"]: f["doi"] = p["doi"]
    return f"@{kind}{{{p['id'].replace('-', '_')},\n" + ",\n".join(f"  {k} = {{{v}}}" for k, v in f.items()) + "\n}"

def build_project(k, pr, pubs):
    ld = {"@context": "https://schema.org", "@type": "ResearchProject", "@id": proj_url(k), "name": pr["name"],
          "alternateName": pr["title"], "identifier": pr["number"], "funder": {"@type": "Organization", "name": pr["funder"]},
          "member": {"@id": f"{BASE}/#person"}}
    title = pr["title"] if not pr["title"].startswith("[") else pr["name"]
    body = f"""<p class="muted">Research project · {e(pr['funder'])}</p><h1>{e(title)}</h1>
<p>{e(pr['name'])} · grant no. {e(pr['number'])} · {e(pr['years'])}</p>
<h2>Publications from this project ({len(pubs)})</h2>{''.join(pub_item(p) for p in pubs)}"""
    (OUT/f"project-{k.lower()}.html").write_text(page(f"{title} | {CFG['name']}", f"Publications from the research project {pr['name']} ({pr['number']}).", body, f"project-{k.lower()}.html", jsonld=ld), encoding="utf-8")

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    global SIDEBAR
    pubs = sorted(PUBS, key=lambda p: (-p["year"], p["title"]))
    by_proj = {k: [p for p in pubs if k in p["projects"]] for k in PROJ}
    SIDEBAR = make_sidebar(pubs, by_proj)
    for p in pubs: build_pub(p)
    for k, pr in PROJ.items():
        if by_proj[k]: build_project(k, pr, by_proj[k])
    # Strona główna
    proj_html = "".join(
        f'<div class="pub"><h3><a href="{proj_url(k)}">{e(pr["title"] if not pr["title"].startswith("[") else pr["name"])}</a></h3>'
        f'<p class="meta">{e(pr["name"])} · {e(pr["number"])} · {len(by_proj[k])} publications</p></div>'
        for k, pr in PROJ.items() if by_proj[k])
    sections = [(t, ts) for _, t, ts in SECTIONS]
    sec = lambda sid, t, ts: f'<h2 id="{sid}">{t}</h2>' + "".join(pub_item(p) for p in pubs if p["type"] in ts)
    pub_html = "".join(sec(*x) for x in SECTIONS if x[0] != "working-papers")
    wp_html = sec(*SECTIONS[3])
    n_oa = sum(1 for p in pubs if pdf_path(p))
    body = f"""<h1>{e(CFG['name'])}</h1><p class="muted">{e(CFG['job_title'])} · {e(CFG['department'])}, {e(CFG['affiliation'])} · {e(CFG['city'])}</p>
<p>{e(CFG['bio'])}</p><p class="meta">Research interests: {e(', '.join(CFG['interests']))}</p>
<p class="meta">{' · '.join(f'<a href="{e(u)}">{n}</a>' for n, u in [("Google Scholar", CFG['google_scholar']), ("RePEc", CFG['repec']), ("ORCID", f"https://orcid.org/{CFG['orcid']}" if CFG['orcid'] else ""), ("University profile", CFG['university_profile'])] if u)}</p>
<p class="meta" id="publications">{len(pubs)} publications · {n_oa} with free full text on this site</p>{pub_html}
<h2 id="projects">Research projects</h2>{proj_html}
{wp_html}"""
    ld = {"@context": "https://schema.org", "@graph": [person_ld(), {"@type": "ProfilePage", "@id": f"{BASE}/", "mainEntity": {"@id": f"{BASE}/#person"}, "dateModified": TODAY}]}
    (OUT/"style.css").write_text(css().strip() + "\n", encoding="utf-8")
    (OUT/"index.html").write_text(page(f"{CFG['name']} — Publications and research projects", CFG["bio"][:155], body, "", jsonld=ld), encoding="utf-8")
    # BibTeX, sitemap, robots, llms.txt
    (OUT/"publications.bib").write_text("\n\n".join(bibtex(p) for p in pubs), encoding="utf-8")
    urls = [f"{BASE}/"] + [pub_url(p) for p in pubs] + [proj_url(k) for k in PROJ if by_proj[k]]
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls) + "\n</urlset>\n", encoding="utf-8")
    (OUT/"robots.txt").write_text("User-agent: *\nAllow: /\n\n# AI crawlers explicitly welcome\nUser-agent: GPTBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\nUser-agent: CCBot\nAllow: /\n\n"
                                  f"Sitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    llms = [f"# {CFG['name']}", "", f"> {CFG['bio']}", "", f"- Affiliation: {CFG['department']}, {CFG['affiliation']}, {CFG['city']}",
            f"- Research interests: {', '.join(CFG['interests'])}", f"- Google Scholar: {CFG['google_scholar']}", "", "## Research projects", ""]
    for k, pr in PROJ.items():
        if by_proj[k]: llms.append(f"- [{pr['name']} ({pr['number']})]({proj_url(k)}): {len(by_proj[k])} publications, funder: {pr['funder']}")
    for t, ts in sections:
        llms += ["", f"## {t}", ""]
        for p in pubs:
            if p["type"] in ts:
                extra = f" DOI: {p['doi']}." if p["doi"] else ""
                llms.append(f"- [{p['title']}]({pub_url(p)}): {p['authors']} ({p['year']}), {p['venue']}.{extra}" + (f" {p['abstract']}" if p.get("abstract") else ""))
    (OUT/"llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    print(f"OK: {len(pubs)} publikacji, {sum(1 for k in PROJ if by_proj[k])} projektów, {n_oa} PDF -> {OUT}")

if __name__ == "__main__":
    main()
