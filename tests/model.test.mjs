import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const edition = JSON.parse(
  readFileSync(new URL("../web/data/edition.json", import.meta.url), "utf8"),
);
import { schoolYear, history } from "../web/model.mjs";
test("entries use the school year ending and keep daily averages separate from enrolment", () => {
  assert.equal(schoolYear(1895), "1894–95");
  const rows = history(
    edition.schools.Langley,
    edition.schools["Langley, East"],
    [1890, 1895],
  );
  assert.equal(rows[1].left.enrolled, 32);
  assert.equal(rows[1].right.daily, 12.85);
  assert.equal(rows[1].left.salary, 50);
  assert.equal(rows[0].left.spending, null);
});
test("a missing school-year remains absent when its comparison school has figures", () => {
  const [row] = history(
    edition.schools["Port Kells"],
    edition.schools.Langley,
    [1890],
  );
  assert.equal(row.left, null);
  assert.equal(row.right.daily, 15.7);
});
