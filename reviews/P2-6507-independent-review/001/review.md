# Independent review 6507

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and 4300F0..43014E span match the locked source. GNU Thumb decoding confirms both nonzero-status branches call 415FAE and then continue. It next makes three calls with fresh `[SP+8]` (42ED60, 42EBAA, 42EFF4), ignoring results in this span, sets R4=0, and branches to 4301B0 outside the mapped range.

The in-span fallback at 43011A stores byte 0 and halfword 3 at the literal base and base+2, then branches to 430192 outside the span. The polling path repeatedly loads the word through the literal at 430230 and extracts bits 20–27, branching back while the extracted byte is zero; no timeout or delay appears here. Once nonzero, it writes 1 at SP+20, stores SP+36 at SP+0 for the fifth argument, and calls 42EE70 with (fresh `[SP+8]`, 0, 0, SP+20, SP+36). Its result is ignored here. The low byte of R4 is then compared to 2; unequal branches to 4301AE, while equal continues outside this span.

No successful-read or initialized-SP+36 assumption is made. The bound, later processing, and external child behavior are outside this packet.

No canonical files or gates changed.
