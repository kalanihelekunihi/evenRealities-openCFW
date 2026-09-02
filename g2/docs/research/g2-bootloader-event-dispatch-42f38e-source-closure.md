# G2 bootloader event dispatcher source closure

Date: 2026-09-01

The stored callback at `0x0041D1B4` targets the complete 76-byte dispatcher at
`0x0042F38E`. It is MIT production C in `runtime_event_dispatch_42f38e.c`.
Event one routes a zero or nonzero state byte to distinct retained providers;
event two writes two image-specific state words; other eight-bit events are
intentional no-ops. Every route returns zero.

Apple clang 21 and Homebrew clang 22 reproduce the authenticated body exactly
after two strict Thumb-call relocations. The Apollo-main analogue at
`0x0059FD36` is byte-for-byte exact. The boot and main literal words differ by
image and remain authenticated outside the function. Portable tests cover all
256 event values, both event-one branches, event-two state writes, and
high-bit truncation to the eight-bit event ABI.

Live callback registration and hardware-service effects are **blocked by
unavailable physical evidence**. No MMIO, flashing, reset, or completeness
claim occurred.
