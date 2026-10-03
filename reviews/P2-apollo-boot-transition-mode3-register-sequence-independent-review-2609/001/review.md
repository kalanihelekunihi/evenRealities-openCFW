# Independent review 2609: mode-3 transition register sequence

**Result: PASS_SCOPED.** `accepted` remains false.

The receipt, source images, referenced static pointer map, and body hashes match. A replay copy redirected to a fresh output directory passes all 192 cases, 96 per entry. The cases cross boost/final flags, inputs 1/2/257, low-10-bit saturation boundaries, and zero/all-one register words.

The independent ordered field-insertion oracle agrees with original enter and exit execution. It verifies low-10 saturation and restoration, optional low-7 saturation/subtraction, gate-bit set/clear order, field updates and input-byte selection, saved-mode restoration, auxiliary bit handling, and final timing selection. Original delay and ITCM instructions run without interception; the calls receive 5 and 10, and the fixed clock fixture produces 145 and 305 loop iterations (450 total). R4-R11, SP, return values, writes and frame are checked.

This covers mode 3 only. Clock/MMIO and flags are stable fixture values; dynamic changes, physical timing, concurrency, and ownership are not established. Other-mode behavior is outside this replay. No canonical admission is claimed.
