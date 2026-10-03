# Independent review 2295

**Result:** PASS_SCOPED.

Isolated replay regenerated all 648 fixtures. Source, body [0x7BC0,0x7CEE), literal span [0x7CF0,0x7CF8), and candidate file hashes match. The composition executes the original 6AC0 path from configuration byte 85 = 0, through 6A80/685C/6608/A324/4480 and mode-5 storage; setup status-bit polling remains clear for the 315-delay timeout, which the caller ignores. The parent’s base control-word clear to 0x7FFCFFFF is asserted, along with subsequent sequence/budget/poll arguments, result/output/status, high registers and SP. All fixture replays pass.

**Limits:** Only the old-mode-zero transition is composed. Setup status and measurement status are modeled, and child register ledgers are not fully asserted by this parent composition. Other old modes, physical timing/MMIO, aliasing and concurrent changes remain unproven; no canonical admission.
