# Rebuild the isolated source candidates

Run from `/Users/kalani/Repo/evenRealities-openCFW`:

```sh
python3 g2/components/main/source_candidate_20261010/build.py
python3 g2/components/touch/source_candidate_20261010/build.py
python3 g2/components/case/source_candidate_20261010/build.py
python3 g2/components/audio/source_candidate_20261010/build_arm_inventory.py
python3 g2/components/bootloader/source_candidate_20261010/build.py
python3 g2/analysis/foundation-source-inventory-20261010/rebuild.py
```

These produce separate source object inventories or archives. They do not generate a deployable six-payload firmware bundle. Touch additionally requires the pinned offline Docker toolchain described in its README. Main, CASE, audio and bootloader require Clang and ARM binutils. Foundation replay requires the exact recorded input/tool identities.

Original-byte comparisons run separately under the existing `/tmp/iar-c-runtime-venv/bin/python` environment. Consult each component report for its verifier and its explicit provider fixture boundary. Compiled source, original behavior comparisons, integrated provider semantics, complete source coverage and whole-payload byte equality are separate evidence categories.

For the current CASE event exports, build the CASE archive first, then run:

```sh
/tmp/iar-c-runtime-venv/bin/python g2/analysis/case-event-set-export-20261010/verify.py
/tmp/iar-c-runtime-venv/bin/python g2/analysis/case-timer-pend-export-20261010/verify.py
```

Both verifiers assert that the compared Clang object is byte-identical to the member in the current archive. The CASE builder also performs an all-member relocatable link, which checks duplicate definitions while leaving unresolved providers visible.

Touch reset source and placement checks are isolated from the 45-unit archive builder. Run the scripts in `g2/analysis/touch-reset-layout-candidate-20261010/` as documented in that report; its `archive_link_results.json` records a relocatable link of the touch archive and reset objects with zero undefined symbols. That link does not place the 964-byte initialized payload into a complete executable image.

Current component counts and remaining-work estimates are recorded in `REPORT.md`. Provider closure rounds can change archive composition and unresolved counts; use fresh receipts from each build rather than this command guide as a status source.
