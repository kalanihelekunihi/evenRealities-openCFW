# Independent review 1869: flash address helpers pass within scope

Status: **PASS_SCOPED**. Accepted: **no**.

Source and artifact pins match. An isolated replay passed all 36 fixtures and exactly reproduced the submitted `replays.json`.

Decoded `8C74` independently: addresses below `0x10000` require 128-byte alignment; larger addresses add `0xF0000E00` modulo 32 bits, must then be below 512, and must be aligned. This yields the aligned upper accepted range `[0x0FFFF200, 0x0FFFF400)`, with address zero accepted. `8CA8` shifts low addresses by seven; otherwise it applies the same wrapped addition and shifts, without validating alignment or range. Literal words at `8CA4` and `8CC0` both contain `0xF0000E00`; neighboring alignment is excluded.

The packets establish instruction behavior only. Physical flash addressability, resident ROM semantics, and broader caller contracts remain unresolved; no canonical admission is made.
