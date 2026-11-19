export const schoolYear = (ending) =>
  Number(ending) - 1 + "–" + String(ending).slice(-2);
export function history(a, b, years) {
  return years.map((year) => ({
    year,
    left: a.years[year] ?? null,
    right: b.years[year] ?? null,
  }));
}
