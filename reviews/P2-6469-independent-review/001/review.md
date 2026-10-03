# Independent review 6469

Disposition: **PASS_SCOPED**; `accepted:false`.

The F41A..F4B2 packet/source hashes match. GNU Thumb decoding confirms a frameless leaf with a two-stage gate: it first tests a fresh state byte for 0x21 and, only on equality, freshly checks a second word for zero. If that short-circuit condition does not select capture, it freshly rereads the state and captures only when its low byte is unsigned >=0x22. Otherwise it writes the fallback bytes.

Capture mode publishes six extracted bytes in order: hardware word bits25..29; a fresh reread of that same word's bits11..15; another word's bits8..12; another word's bits17..21; a fresh word's bits25..29; then a fresh reread of that word's bits11..15. The byte destinations are individually literal-backed. Fallback mode writes 14, 31, 21, 31, 11, 11 to those six destinations in the same order. Both paths return zero through BX LR.

The repeated hardware-word reads and byte-store order are preserved; no snapshot or atomicity is assumed. No field purpose or admission claim is made, and canonical files/gates are unchanged.
