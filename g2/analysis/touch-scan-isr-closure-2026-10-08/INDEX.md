# Latest touch reconstruction navigation

| Family | Source/evidence | Validation |
|---|---|---|
|ISR/active+LP FIFO/continuation/completion/dispatch|scan_isr_offline/isr.c,h; REPORT.md|1,636 cases; no call stubs; synthetic peripherals|
|Preparation and clock source|../touch-scan-preparation-closure-2026-10-08/INDEX.md|1,931 fresh cases;42 exact public-helper bytes|
|Base/mode/all-slot and auto-dither|../touch-auto-dither-closure-2026-10-08/INDEX.md|Earlier base/dither suites and preserved144 all-slot cases|
|Earlier source and attribution|../touch-mode-closure-2026-10-08/INDEX.md|Individual composition limits;208 exact PDL bytes|

ISR public completion attribution adds36 bytes; cumulative distinct demonstrated286 bytes. Whole firmware/source completion remains unproven. build_offline.py and verify.py reproduce the new comparator; screen_public_completion.py reproduces the selected public-function match from pinned source. An actual project-entry test uses reset-copied context pointers; it remains a direct synthetic call.

Next: LP history processing and actual buffer sizing/configuration. Physical timing/IRQ delivery and unknown external callback bodies are not closed. No commits/index/device writes.
