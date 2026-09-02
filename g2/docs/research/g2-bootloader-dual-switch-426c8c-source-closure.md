# G2 bootloader dual-clock switch source closure

The authenticated bootloader entry at
`[0x00426C8C,0x00426CCC)` switches bit 5 of CLKGEN register
`0x40004044` from the low input byte. A zero input clears the bit and
returns success. A nonzero input returns success immediately when the bit is
already set; otherwise it publishes the bit and calls the retained bounded
status provider at `0x0041D246` with delay 100, status register
`0x40004030`, mask/expected value `0x01000000`, and final argument 1.

`runtime_dual_switch_426c8c.c` expresses that contract as freestanding
clean-room MIT C. Apple clang 21.0.0 and Homebrew clang 22.1.8 emit the same
56-byte Thumb body after its one strict `R_ARM_THM_CALL` relocation at
offset 36:

- relocated SHA-256:
  `877df9e6e2cba9faa0c6435ae1aea24d3b3162b3a0613947c1a81154a9059426`;
- unrelocated SHA-256:
  `3a619bebf32afbd0f49259f3806b0d96b4024b70eab48eb36b621ef0d54def0f`;
- authenticated stock-prefix SHA-256:
  `d5b82fd57ea541895d00b663f98123f4999e8a71c722a9392af2172cf31cd359`.

The final eight stock bytes at `[0x00426CC4,0x00426CCC)` are retained as
an authenticated unreachable tail, SHA-256
`d7d2a4025d26ea346c59aacce99c433ac393769f80658c1d6586235cda9af704`.
There is no direct or stored ingress to that tail or any interior halfword of
the source entry. The three direct call sites remain `0x00421FB4`,
`0x00421FDE`, and `0x004220A4`.

Host tests cover low-byte truncation, redundant enable, enable-and-poll,
disable, register-bit preservation, exact provider arguments, and status
propagation. The exhaustive post-MSPI ledger now admits 1,850 production
source bytes and retains 12 unreachable-tail bytes with zero unclassified
bytes.

Canonical Apple/Linux providers are 163,840/163,824 bytes with SHA-256
`13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b`
and
`11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875`.
The complete packages are 4,749,540/4,749,524 bytes with SHA-256
`aeb58283e5ab4383be2b3ca258e789028b9259a524b936d5d5a5187ba1035b54`
and
`b1587219ffa1153ff3b53af5774e66d86fbb2a0e1cacc35b093cdd34d39e1e58`;
both have zero unresolved flash regions.

No MMIO, clock, reset, signing, transmission, erase, or flash operation was
performed. Live oscillator, status-transition, timing, and cold-boot
qualification is blocked by unavailable physical evidence. Firmware-wide
functional completeness is not claimed; the next executable software
frontier begins at `0x00426CCC`.
