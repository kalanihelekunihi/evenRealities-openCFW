# Independent review 2235

**Result:** PASS_SCOPED.

The source hash and both body hashes match the receipt: row reset `[0x5868,0x58F6)` and fill leaf `[0xA9D4,0xA9E4)`. Decoding the fill bytes independently gives `R3=R0`, `R2=R0+R2` modulo 32 bits, then `CMP R3,R2; BNE store; BX LR`; the loop stores the low byte of R1 and increments R3 until it reaches the endpoint. Thus R0 is preserved and R2 contains the endpoint. The original 5868 body still has the previously reviewed type gates and field effects.

An isolated replay regenerated all 486 rows with no function interception. The fill executes as original instructions. The recorded A9D4 arguments match timer pointer, byte value, and twice the saved count; the verified timer bytes cover fill lengths 0, 2, and 6. The row-reset item/parameter/history checks and R4/SP preservation also pass.

**Limits:** This verifies only the bounded zero-, two-, and six-byte fill cases and the tested row configurations. It does not establish arbitrary lengths, address wrap/fault behavior, aliasing, concurrency, or physical meaning. No canonical admission is made.
