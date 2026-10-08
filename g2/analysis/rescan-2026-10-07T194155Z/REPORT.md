# OpenCFW change scan — 2026-10-07 19:41 UTC

Compared with the saved 18:58 UTC scan. Read-only inspection; only this report and snapshot were created. No builds, generators, test execution, firmware edits, staging or campaign changes.

Component source counts remain **302 bootloader and 89 foundation**. Change counts: {'unchanged': 391}; removals: 0. New reconstructed C/header work is in the analysis-owned idle-sleep-policy, idle-timer-chain, idle-lifecycle-native and idle-native-integrated directories, listed in the snapshot. None of these inspected source files matches a Git ignore rule. Build artifacts remain separately ignored.

The earlier QEMU partial failure has advanced to **nine PASS scenarios**, including outgoing and incoming floating-point context fixtures. This is an MPS3 Cortex-M55 architecture harness, not an Apollo510 peripheral or hardware validation.

The sleep-policy receipt reports **259 PASS cases**, timer-chain **205**, and native lifecycle **528**. The new **214-object** candidate `badad5a92beec12dd1f5389033d51db87aa8d5bb77cb3410a7e465f2aa649b57` independently matches its recorded ELF hash. Its exact-image chain receipt reports **528 PASS cases** and its installed-bootstrap receipt **six PASS cases**. Available integration receipts are normal/update **two PASS** and malformed-input **three PASS**. No power-loss receipt or completed full regression summary exists in this candidate's validation directory at scan time; do not call all seven integration cases complete.

These results compare bounded original-instruction fixtures with reconstruction. Timer/power behavior, external-call contracts and synthetic wake assumptions remain limits; they do not establish whole-system scheduling, hardware sleep correctness or source/byte-identical bundle completion. Passing cases are not a coverage percentage.

Shared offline ELF remains `129a6b2f38f145f33e791874f52d722fb1715d5fff5c957a285644312f34a6f9`. The 209-object predecessor is preserved. The new candidate is a separate test layout with a third code slot and is not a deployable or promoted firmware image. No completed power-loss receipt is a scan-time observation, not evidence of test failure.

Exact paths, source hashes, receipt hashes and Git status counts are in [snapshot.json](snapshot.json). Receipt status was inspected, not rerun in this scan.
