# G2 teleprompt controller dependency boundary

Seven retained-path anchors / 1,752 bytes expand to ten functions / 2,408 body
bytes for `app\gui\teleprompt\teleprompt.c`. The physical object is
`[0x005899A4,0x0058A8E0)`, 3,900 bytes. Two source-order event handlers at
`0x00589EB6` and `0x00589FE6` were restored beyond Ghidra.

The object has 162 direct calls and no indirect call. All 149 external calls
terminate at admitted EasyLogger (90), bounded IAR/EABI runtime (4), LVGL (2),
exact CMSIS-FreeRTOS v10.5.1 wrappers (7), nanopb (3), or bounded first-party
teleprompt providers (43). It reuses commits `a596b264…`, `344c7c318…`,
`d213f261…`, and `98bf4db6…`; no reusable text engine, dependency definition,
version discriminator, or private generating commit is exposed.

Ingress closes over 37 BL sites and three stored function pointers. A raw BL
lookalike at `0x0057F460` starts on the second halfword of the valid four-byte
`mul` at `0x0057F45E`, so it is not callable strict-interior ingress. Remaining
work is first-party controller recreation and hardware/UI validation; the
object is not production-routed.
