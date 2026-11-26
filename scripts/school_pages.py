"""Build readable school histories from the same edition as the comparison tool."""
from html import escape
import json
import re
from urllib.parse import urlencode
import xml.etree.ElementTree as ET


def school_year(ending):
    return f"{int(ending) - 1}–{str(ending)[-2:]}"


def display_name(name):
    return name.replace(", East", " East")


def compare_url(name, year):
    return "../../#" + escape(urlencode({"school": name, "year": year}), quote=True)


def write_school_pages(stage, tool):
    edition = json.loads((stage / "data/edition.json").read_text(encoding="utf-8"))
    base = "https://coolcode.ca" + tool["url"]
    paths = {}
    for name, school in sorted(edition["schools"].items()):
        if not school["years"]:
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        path = "schools/" + slug + "/"
        if not slug or path in paths.values():
            raise ValueError(f"School needs a unique URL: {name}")
        paths[name] = path
    if not paths:
        raise ValueError("No school histories to publish")

    def school_links(prefix, exclude=None):
        return "\n".join(f'<li><a href="{prefix}{path}">{escape(display_name(name))}</a></li>'
                         for name, path in paths.items() if name != exclude)

    sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    collection_url = base + "schools/"
    ET.SubElement(ET.SubElement(sitemap, "url"), "loc").text = collection_url
    directory_rows = []
    report_year = str(edition["end"])
    for name, path in paths.items():
        school = edition["schools"][name]
        label = escape(display_name(name))
        years = sorted(school["years"], key=int)
        last = years[-1]
        recent = school["years"][last]
        period = school_year(years[0]) + " to " + school_year(last) if len(years) > 1 else school_year(last)
        finding = (f'In {school_year(last)}, {label} enrolled {recent["enrolled"]:,} pupils '
                   f'and averaged {recent["daily"]:.2f} pupils present each day.')
        report_row = school["years"].get(report_year)
        enrolled = f'{report_row["enrolled"]:,}' if report_row else "—"
        daily = f'{report_row["daily"]:.2f}' if report_row else "—"
        directory_rows.append(f'<tr><th scope="row"><a href="../{path}">{label}</a></th>'
                              f'<td>{period}</td><td>{enrolled}</td><td>{daily}</td></tr>')
        rows = []
        for year in reversed(years):
            result = school["years"][year]
            rows.append(f'<tr><th scope="row"><a href="{compare_url(name, year)}">{school_year(year)}</a></th>'
                        f'<td>{result["enrolled"]:,}</td><td>{result["daily"]:.2f}</td></tr>')
        finances = []
        if recent.get("spending") is not None:
            finances.append(f'annual school expenditure of ${recent["spending"]:,}')
        if recent.get("salary") is not None:
            finances.append(f'a monthly teacher salary of ${recent["salary"]:,}')
        money = f'<p>For {school_year(last)}, the report lists {" and ".join(finances)}.</p>' if finances else ""
        source = escape(edition["source"] + "#page=" + str(school["page"]), quote=True)
        canonical = base + path
        title = f"{label} school enrolment and attendance, {period}"
        directory = stage / path
        directory.mkdir(parents=True)
        nearby = ""
        if name == "Aldergrove":
            nearby = '<p><a href="https://coolcode.ca/postmarkplaces/">Look up the Aldergrove post office in Postmark Places</a> to trace the same community’s postal history.</p>'
        page = f"""<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · CoolCode</title><meta name="description" content="{finding} See the annual figures and the original BC report.">
<link rel="canonical" href="{canonical}"><link rel="stylesheet" href="../../style.css">
<script defer src="/assets/tool-metrics.js" referrerpolicy="no-referrer"></script></head>
<body><header><div class="wrap"><nav aria-label="Site"><a href="https://coolcode.ca/">CoolCode.ca</a><a href="../../">Schoolhouse Ledger</a></nav>
<div class="mast"><h1>{label} school records</h1><p>{finding}</p><a href="{compare_url(name, last)}">Compare {label} with another school</a></div></div></header>
<main class="wrap"><section><h2>Attendance, {period}</h2><p>Enrolment counts pupils registered during the school year. Daily attendance is the average number present on a school day. Select a year to compare schools.</p>
<table><thead><tr><th scope="col">School year</th><th scope="col">Pupils enrolled</th><th scope="col">Average daily attendance</th></tr></thead><tbody>{''.join(rows)}</tbody></table>{money}</section>
<section><h2>Original school report</h2><p>The Twenty-fourth Annual Report of the Public Schools of British Columbia lists this school as “{escape(name)}”. <a href="{source}">Read printed page {school['printed']} (PDF page {school['page']})</a>.</p></section>
<section><h2>Other schools in the report</h2><p><a href="../">Browse all school histories and their report-year figures</a></p><ul>{school_links("../../", name)}</ul>{nearby}</section></main></body></html>
"""
        (directory / "index.html").write_text(page, encoding="utf-8")
        ET.SubElement(ET.SubElement(sitemap, "url"), "loc").text = canonical
    period = school_year(report_year)
    total_rows = sum(len(edition["schools"][name]["years"]) for name in paths)
    coverage = f'{len(paths)} schools and {total_rows} documented school-years'
    collection = f"""<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Historic Lower Mainland school attendance records · CoolCode</title>
<meta name="description" content="Compare {period} enrolment and daily attendance across historic Langley and Surrey schools, then open each school’s annual records and original report page.">
<link rel="canonical" href="{collection_url}"><link rel="stylesheet" href="../style.css">
<script defer src="/assets/tool-metrics.js" referrerpolicy="no-referrer"></script></head>
<body><header><div class="wrap"><nav aria-label="Site"><a href="https://coolcode.ca/">CoolCode.ca</a><a href="../">Schoolhouse Ledger</a></nav>
<div class="mast"><h1>Historic Langley and Surrey schools</h1><p>Explore {coverage} in British Columbia’s public schools report. Open a school name to see its attendance history and original printed page.</p></div></div></header>
<main class="wrap"><section><h2>Schools in the {period} report</h2><p>Enrolment counts pupils registered during the year. Daily attendance is the average number present on a school day.</p>
<div class="scroll" tabindex="0" role="region" aria-label="School records table"><table><thead><tr><th scope="col">School</th><th scope="col">Years documented</th><th scope="col">{period} enrolment</th><th scope="col">{period} daily attendance</th></tr></thead><tbody>{''.join(directory_rows)}</tbody></table></div></section>
<section><h2>Read the report</h2><p><a href="{escape(edition['source'], quote=True)}">Read the digitized Twenty-fourth Annual Report of the Public Schools of British Columbia</a> or <a href="../">compare two schools in the ledger</a>.</p></section></main></body></html>
"""
    (stage / "schools/index.html").write_text(collection, encoding="utf-8")
    ET.ElementTree(sitemap).write(stage / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    return school_links("./")
