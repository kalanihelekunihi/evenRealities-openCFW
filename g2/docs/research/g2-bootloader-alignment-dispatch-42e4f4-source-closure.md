# G2 bootloader alignment dispatcher source closure

Date: 2026-09-01

The complete 26-byte function at `0x0042E4F4` is MIT production C in
`runtime_alignment_dispatch_42e4f4.c`. It rejects lengths not divisible by 16
or destination values not divisible by four with `0x08000140`; otherwise it
forwards all four arguments to the retained provider at `0x0042E4A0`.

Apple clang 21 and Homebrew clang 22 reproduce the authenticated body exactly
after one strict Thumb-call relocation. The Apollo-main analogue at
`0x004D0A2C` is byte-for-byte exact, including the external error literal.
Portable tests cover aligned dispatch and every low-bit rejection class.

Actual accelerator/DMA behavior behind the retained provider is **blocked by
unavailable physical evidence**. No MMIO, flashing, reset, or completeness
claim occurred.
