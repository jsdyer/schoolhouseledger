# Schoolhouse Ledger

Compare historical school enrolment and average daily attendance around Langley and Surrey. The source links open each school’s individual page in the provincial report.

[Open Schoolhouse Ledger](https://coolcode.ca/schoolhouseledger/)

## Try it

<!-- coolcode:guide -->
In 1894–95 Langley enrolled 32 pupils and averaged 19.79 present each day. Langley East enrolled 23 and averaged 12.85. Earlier attendance tables and the report-year financial figures cover different periods.
<!-- /coolcode:guide -->

## School histories

The [school index](https://coolcode.ca/schoolhouseledger/schools/) links to a readable history for each school with documented figures. Each page includes its annual figures and the printed report page. Selecting a school year opens that school and year in the comparison tool. The build regenerates these pages and their [sitemap](https://coolcode.ca/schoolhouseledger/sitemap.xml) from the published edition.

## Sources and interpretation

The 24th annual report of BC public schools contains a short account and a table of earlier attendance for each school. This edition includes 38 entries spread across seven schools from 1889–90 through 1894–95. The schools are Aldergrove, Cloverdale, Langley, Langley East, Mud Bay, Port Kells and Surrey Centre. Each school keeps its historical name. The year selector uses the school year ending in the displayed spring or summer.

The original page numbers and the PDF viewer’s page numbers differ. Each record retains both. The transcription stores a missing school-year and an absent financial figure separately from a recorded zero. Financial figures apply only to 1894–95. A daily average below enrolment does not establish how many days any individual pupil attended.

[Digitized provincial report](https://archive.org/details/annualreportonpu2418brit) · [Transcribed school rows](sources/schools.csv)

## Refresh and verification

Monthly. The importer retrieves the Internet Archive scan, with a byte-identical Wikimedia Commons copy available if the first host is unavailable. It verifies the reviewed scan and validates the keyed school-year transcription using the Python standard library. The retrieval date records the last successful source check in UTC. The coverage on the homepage and in the tool describes the underlying records. A changed archive requiring review or a failed download leaves the previous edition available. The scheduled workflow validates the data, runs the tests and publishes the resulting snapshot. For a manual refresh, run `python3 scripts/refresh.py`.

The interface, selections and CSV exports run locally in the browser. Visiting a source or map link opens the publisher’s site. The offline build uses the checked-in edition. To build and preview it, run the following commands.

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

The Pages workflow also exercises the tool in Chromium at its project subpath and checks the mobile layout. Update the source sentence in `tool.json` and the marked guide above when changing coverage or interpretation.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
