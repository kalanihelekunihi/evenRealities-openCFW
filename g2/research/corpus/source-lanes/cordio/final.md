Implemented a narrow, production-excluded Cordio recovery increment. No firmware blobs, production overlays, or manifests were modified.

Modified files:

- [analyze_g2_cordio_source_map.py](/var/tmp/opencfw-source-lanes.l5hz6p/cordio/openCFW/tools/analyze_g2_cordio_source_map.py) — fail-closed authenticated mapping analyzer.
- [test_analyze_g2_cordio_source_map.py](/var/tmp/opencfw-source-lanes.l5hz6p/cordio/openCFW/tests/test_analyze_g2_cordio_source_map.py) — parser, boundary, and full-corpus tests.
- [cordio-source-path-function-map.md](/var/tmp/opencfw-source-lanes.l5hz6p/cordio/openCFW/docs/research/cordio-source-path-function-map.md) — evidence, boundaries, uncertainty, and blockers.
- [progress.md](/var/tmp/opencfw-source-lanes.l5hz6p/cordio/openCFW/docs/progress.md) — current census and scope update.

Evidence pinned:

- 36 retained Cordio translation-unit paths.
- 32 paths with function anchors; four without.
- 114 distinct anchored functions.
- 22 public-Packetcraft candidates, five Ambiq ports, nine Ambiq/application-or-Even paths.
- Map SHA-256: `772063dc1841dc33523e68ecca9188923e28efd5cbe6db5a22a36979c41b2623`.
- Per-anchor bounds, call topology, small constants, and diagnostic/assert line values.
- Public r20.05–r20.05c interval remains limited to the existing ATT/DM and unchanged-blob evidence; no exact vendor-tree claim.

Validation:

- All 24 focused tests passed.
- Cordio snapshot verifier passed.
- Full authenticated analyzer replay passed.
- Python compilation and changed-file whitespace checks passed.
- `git diff --check` was unavailable because this isolated copy contains no functional Git repository metadata.

No new function had complete ABI, caller, relocation, boundary, and behavioral closure. Promotion remains blocked by the missing authenticated Ambiq Cordio archive, exact build configuration/layouts, and per-function exterior-reference closure.