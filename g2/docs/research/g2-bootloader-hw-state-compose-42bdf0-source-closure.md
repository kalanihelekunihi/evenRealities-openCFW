# G2 bootloader stored-entry hardware-state composer source closure

The authenticated interval `[0x0042BDF0,0x0042BF4E)` is now production-routed
from `runtime_hw_state_compose_42bdf0.c`. Apple clang 21 and Homebrew clang 22
both reproduce the exact 350-byte stock body, SHA-256
`6abb107b7aebe13eaff37f34185f8865b71f27c756f8214d3646efa4f2304c1c`,
after four strict Thumb-call relocations. The function has no direct call site;
its authenticated entry is the Thumb pointer stored at `0x0041D164`. No
interior entry gained ingress. The Apollo-main analogue at `0x005A1C18`
matches 313 of 350 bytes.

The portable model covers the readiness gate, all three configuration-read
failures, sixteen-word primary copy, four-word secondary copy, tertiary value,
four low-seven-bit overlays, averaged and forwarded packed fields, terminal
magic `0x1F01600D`, and the commit call. The three read edges target
`0x00421548`; the commit edge targets `0x0041CC04`. Four image-local state and
MMIO literals are pinned.

Offline compilation, portable behavior, provider identity, manifest ownership,
and unsigned firmware assembly are verified. Live configuration storage,
retained SRAM, MMIO readiness, packed hardware-state interpretation, commit
effects, concurrency, reset, and cold boot are blocked by unavailable physical
evidence. No signing, flashing, reset, or hardware access occurred, and
functional completeness is not claimed.
