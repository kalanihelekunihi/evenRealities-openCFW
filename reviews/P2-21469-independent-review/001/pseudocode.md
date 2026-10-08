# Object setup with three-byte stack readback

Partial/unaccepted. Exact 102 instruction bytes 484C38..484C9E, continuing open 32-byte frame at484A98, object R4. Call 4D4ABC(object+76,object+888,live R2/R3). Call 488198(object+88,live remaining registers), then 4D48C4(object+88,255,live R2/R3). Similarly call 488198(object+64), then 4D48C4(object+64,255).

Call 439BE4(SP,object+48,3), then load full word SP0 into R1 and call 4D48AA(object+64,R1,live R2/R3). Call 439BE4(SP,object+51,3), load full SP0 into R1, call 4D4A2E(object+64,R1,live R2/R3). These copies replace only three bytes of the stack word if the helper follows the observed copy contract; the fourth byte is retained from previous SP0 contents, not freshly cleared. Earlier local initialization set SP0=0 before paired setup, but helper effects on stack memory need a whole-function contract before asserting that high byte always zero. Preserve the full-word read and partial copy explicitly.

Fresh word[object+28] into R1; call 4D4A48(object+64,R1,live R2/R3). Frame remains open; byte+40 selection begins next. Helper contracts remain unresolved. No C, freeze, whole coverage or equality claim.
