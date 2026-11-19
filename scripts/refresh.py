"""Publish the checked transcriptions after verifying the archived school report."""
import csv
from source_io import ROOT, archives, archived, publish


def assemble():
    schools = {}
    with (ROOT / "sources/schools.csv").open() as raw:
        for row in csv.DictReader(raw):
            end, enrolled = int(row["year_ending"]), int(row["enrolled"])
            attendance = float(row["average_daily"])
            school = schools.setdefault(row["school"], dict(page=int(row["pdf_page"]), printed=int(row["printed_page"]), years={}))
            if end in school["years"] or not 0 <= attendance <= enrolled or school["page"] != int(row["pdf_page"]):
                raise ValueError("Invalid school-year record")
            school["years"][end] = dict(enrolled=enrolled, daily=attendance,
                spending=int(row["expenditure"]) if row["expenditure"] else None,
                salary=int(row["salary_month"]) if row["salary_month"] else None)
    years = sorted({y for school in schools.values() for y in school["years"]})
    if not all(1895 in school["years"] for school in schools.values()):
        raise ValueError("Incomplete report-year coverage")
    return dict(start=years[0], end=years[-1], years=years, coverage="School years 1889–90 to 1894–95",
                count=sum(len(s["years"]) for s in schools.values()), schools=schools, source=archives()[0]["url"])


if __name__ == "__main__":
    archived(archives()[0])
    publish(assemble())
