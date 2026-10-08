# Touch EEPROM offline reconstruction

Canonical home for independently reconstructed touch callback, deferred persistence, flash providers and EEPROM history/read/write source. Promoted from bounded analysis, with original evidence preserved. This module is **not linked into production firmware or the accepted bootloader checkpoint** and is not a deployable storage library.

See `PROVENANCE.json` for locked image identities, original address ranges and ownership. Offline build and original-instruction comparison scripts live in `g2/analysis/touch-read-closure-2026-10-08`. Fixed guest addresses, raw arithmetic, borrowed-buffer callbacks and stock error discard intentionally preserve observed behavior. Do not use these as a new application API.

Write scope requires physical row and step both128 bytes. Generic subrow read/modify/write, malformed contexts/payloads, concurrent mutation and physical SROM execution are outside the validated contract. Read scope will be documented by the accompanying comparison report. No byte-identical compilation claim.
