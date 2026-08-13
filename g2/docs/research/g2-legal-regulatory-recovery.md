# G2 legal/regulatory UI recovery

`legal_regulatory.c` closes as one 234-byte event handler plus a 194-byte
content/literal pool, for 428 physical bytes at `[0x005BF7B8,0x005BF964)`.
The next function is the already audited EasyLogger async-sink callback, not
part of this object. Two stored references and one direct call enter compiler-
shared diagnostic tails at `0x005BF880`/`0x005BF88C`; these multi-entry tails
are explicitly pinned rather than misclassified as separate functions.

The handler owns the complete regional legal-string table and startup,
scroll, and exit dispatch. Its 15 calls resolve to ten admitted EasyLogger,
one admitted LVGL scroll primitive at selected commit `344c7c3…`, two bounded
IAR memory primitives, and two first-party page/animation providers. No opaque
third-party body or new version discriminator remains; it is not production-routed.
