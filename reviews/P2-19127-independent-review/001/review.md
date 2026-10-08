# P2-19127 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x4699E0–0x469A76 (150 bytes, 58 instructions); candidate instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the threshold-action diagnostic group and SP+12 byte store of 255, which preserves the upper bytes of the saved R3 word. The child receives SP+12 with arguments (266, 1, 0); its full result is tested and retained for the distinct result-diagnostic group. The shared branch sets R0=0. Diagnostics overwrite saved argument slots, while writes through the supplied pointer remain possible; no immutability or child contract is inferred.
