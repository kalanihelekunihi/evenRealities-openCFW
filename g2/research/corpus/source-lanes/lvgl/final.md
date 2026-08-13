Implemented a narrow, fail-closed LVGL source-recovery increment without modifying the production overlay.

Modified files:

- [analyze_g2_lvgl_source_mapping.py](/var/tmp/opencfw-source-lanes.l5hz6p/lvgl/openCFW/tools/analyze_g2_lvgl_source_mapping.py)
- [test_analyze_g2_lvgl_source_mapping.py](/var/tmp/opencfw-source-lanes.l5hz6p/lvgl/openCFW/tests/test_analyze_g2_lvgl_source_mapping.py)
- [lvgl-version-recovery-audit.md](/var/tmp/opencfw-source-lanes.l5hz6p/lvgl/openCFW/docs/research/lvgl-version-recovery-audit.md)
- [progress.md](/var/tmp/opencfw-source-lanes.l5hz6p/lvgl/openCFW/docs/progress.md)

Evidence pinned:

- Maps only `lv_iter_create` to `src/misc/lv_iter.c`.
- Complete boundary: `0x005C3B00..0x005C3BB2`, 178 bytes.
- Firmware span SHA-256: `847ee3df…81655f`.
- Retained path: `0x006E8794`, referenced through pointer cell `0x005C3BC4`.
- Vendored Git blob: `cb6377c0b50060710e5446dce5d083bfe3bed539`.
- Correlates 28-byte allocation, field offsets, optional context allocation, and assertion lines 65, 68, and 79.
- Explicitly rejects whole-file ownership and production eligibility.

Validation:

- 20 focused analyzer tests passed.
- LVGL snapshot verification passed.
- Python compilation and trailing-whitespace checks passed.
- `git diff --check` was unavailable because this isolated copy contains no usable Git metadata.

Blocker: no direct caller appears in the authenticated decompilation corpus, but indirect reachability and original relocation/caller closure remain unresolved. Therefore no source candidate or production manifest change was made.