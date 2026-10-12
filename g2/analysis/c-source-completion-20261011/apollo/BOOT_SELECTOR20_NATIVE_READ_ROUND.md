# Boot PCM22 selector 20 native read audit

The retained decompiler body for `0x429b4c` does not display reads from its
`current` profile pointer because the extracted byte/word values are dead.
The actual Thumb body computes that pointer at `0x429b60..0x429b64` and
loads its byte at `0x429b94` and word at `0x429b9a`. Selected
`opencfw_spot_pcm22_transition20` already performs both volatile reads.
Deleting them would change the native memory-access and possible fault
behavior, so no selected C change was made. The source SHA-256
`11939afe1885cc7de6ae909e0129b0035963d09dbd3aedea685ac129024a8337`
equals the hash recorded by the prior coherent target receipt.

The complete selector-20 timer/state/temp/core flow is now an explicit
reviewed binding in `manual_body_bindings.json`. Selector 16 `0x42962c` has
the same native/decompiler difference: direct Thumb loads current-profile
byte and word at `0x429674`/`0x42967a`, which selected C also reads. Its
timer, state and trim writes and ambient high return are bound as a complete
body. Rooted header-only proof leads are **168/654**, down from 170; the
whole-catalogue header-only queue is **266/903**. These are attribution
counts, not missing body counts.
No new target build is needed because selected source is hash-identical to
`boot-coplacement-selector17-reread-round/receipt.json` (373 selected units,
1,010 providers, three ROM imports). Runtime equality, ROM behavior and
whole-image data/layout remain open.
