import {
  byId,
  choices,
  number,
  sourceLink,
  table,
  downloadCsv,
  loadEdition,
  failed,
} from "./ui.mjs";
import { history, schoolYear } from "./model.mjs";
try {
  const data = await loadEdition("school-year records");
  const names = Object.keys(data.schools).sort();
  for (const id of ["first", "second"])
    choices(
      id,
      names.map((s) => [s, s.replace(", East", " East")]),
    );
  choices(
    "year",
    data.years.map((y) => [y, schoolYear(y)]),
  );
  function readSelection() {
    const params = new URLSearchParams(location.hash.slice(1));
    const first = names.includes(params.get("school")) ? params.get("school") : "Langley, East";
    const second = names.includes(params.get("compare")) ? params.get("compare")
      : first === "Langley" ? "Langley, East" : "Langley";
    const year = Number(params.get("year"));
    byId("first").value = first;
    byId("second").value = second;
    byId("year").value = data.years.includes(year) ? year : data.end;
  }
  readSelection();
  let csv;
  const money = (n) => (n == null ? "—" : "$" + number(n));
  function render() {
    const ids = [byId("first").value, byId("second").value],
      year = +byId("year").value;
    const pair = ids.map((k) => data.schools[k]);
    const selected = pair.map((s) => s.years[year]);
    const labels = ids.map((s) => s.replace(", East", " East"));
    byId("finding").textContent = selected
      .map((r, i) =>
        r
          ? labels[i] +
            " enrolled " +
            r.enrolled +
            " pupils and averaged " +
            number(r.daily) +
            " present per day."
          : labels[i] + " has no entry for " + schoolYear(year) + ".",
      )
      .join(" ");
    function cells(key, format = number) {
      return selected.map((r) => (r && r[key] != null ? format(r[key]) : "—"));
    }
    table(
      "comparison",
      ["Measure", ...labels],
      [
        ["Pupils enrolled", ...cells("enrolled")],
        ["Average daily attendance", ...cells("daily")],
        ["Reported annual expenditure", ...cells("spending", money)],
        ["Monthly teacher salary", ...cells("salary", money)],
        [
          "Source page",
          ...pair.map((s) =>
            sourceLink(
              "Printed p. " + s.printed,
              data.source + "#page=" + s.page,
            ),
          ),
        ],
      ],
    );
    const h = history(...pair, data.years);
    table(
      "annual",
      [
        "School year",
        labels[0] + " enrolled",
        "Daily average",
        labels[1] + " enrolled",
        "Daily average",
      ],
      h.map(({ year, left, right }) => [
        schoolYear(year),
        left?.enrolled ?? "—",
        left?.daily ?? "—",
        right?.enrolled ?? "—",
        right?.daily ?? "—",
      ]),
    );
    csv = [
      [
        "school",
        "year_ending",
        "enrolment",
        "average_daily_attendance",
        "expenditure_CAD",
        "monthly_teacher_salary_CAD",
        "source",
      ],
    ];
    ids.forEach((s, i) =>
      Object.entries(pair[i].years).forEach(([y, r]) =>
        csv.push([
          s,
          y,
          r.enrolled,
          r.daily,
          r.spending,
          r.salary,
          data.source + "#page=" + pair[i].page,
        ]),
      ),
    );
  }
  byId("csv").onclick = () => downloadCsv("school-comparison.csv", csv);
  document.querySelector("main").addEventListener("change", () => {
    const params = new URLSearchParams({
      school: byId("first").value, compare: byId("second").value, year: byId("year").value,
    });
    window.history.replaceState(null, "", "#" + params);
    render();
  });
  window.addEventListener("hashchange", () => {
    if (!location.hash || new URLSearchParams(location.hash.slice(1)).has("school")) {
      readSelection();
      render();
    }
  });
  render();
} catch {
  failed();
}
