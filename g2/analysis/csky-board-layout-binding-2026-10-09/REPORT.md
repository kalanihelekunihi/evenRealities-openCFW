# Codec board layout and audio-output interface

Static original-byte/source binding PASS; no C-SKY instruction execution or source rebuild is claimed. Hashes, exact decoder commands and eight consumer checks are in [results.json](results.json). The 240-byte configuration is data, not new executable coverage.

The getter at `0x10203004` returns `0x200269A4`. The reviewed normal loader profile stores the matching bytes at `0x100269A4` (codec payload offset `0x189B8`). Authentic SDK linker/loader sources express a paired IRAM/DRAM offset contract; physical visibility between those addresses remains unverified. All field interpretations below are conditional on that contract and the public 32-bit layout.

| Field | Offset | Observed interpretation |
| --- | --- | --- |
| Input source | 0 | PDM (enum 2) |
| Three input configurations | 4, 32, 60 | 28 bytes each; flags 0x498, 0xC98, 0x498 |
| Output mask | 88 | 6: PCM1 and LOGFBANK |
| SADC / PDM configuration | 92 / 96 | One word each |
| I2S input | 100 | 24 bytes |
| PCM0 / PCM1 | 124 / 148 | Six words each |
| LOGFBANK | 172 | Five words |
| I2S output | 192 | Seven words |
| Spectrum | 220 | Five words |

PDM flags encode PGA 24, gain enum 2 and stereo tracking. The public header names gain 2 as 12 dB; the original diagnostic lookup at `0x1020300C` independently maps enum 2 to 12. Neither fact measures physical gain. PCM1 selects PDM; LOGFBANK selects PDM left.

The output consumer `0x10207070` reads track bits at offsets 5 and 33 and binds PCM1 at offset 148. Its I2S branch passes seven words by value to `0x10204228`: four register arguments from offsets 192–204 and three stack words copied from offsets 208–216. It then calls `0x10204340` with mode 0. Prepared I2S fields specify 16-bit I2S, master, 64FS, 16K, left PDM-left and right PDM-right. Initial output mask 6 does **not** enable this branch (I2S bit 8).

Under this layout, left/right values 1/2 agree with the pinned KWS DMIC initializer and conflict with the acquired unchanged AIoT initializer's SADC 0/0. This constrains lineage; it does not identify an exact producing commit, full Kconfig or live routing. KWS pin: `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`; AIoT pin: `d4aa00943e22f9ddfa424f979fae3ee2a62f5c0b`.

For app/CFW work, distinguish enabled PCM/feature output from prepared I2S configuration. A routing feature needs the actual enable transition and provider behavior; changing a prepared source field alone does not establish an active stream. [layout.h](layout.h) and [pseudocode.c](pseudocode.c) are analysis interfaces, not production replacements.

Remaining boundary: an authenticated chip memory-alias contract or visibility trace is needed to establish physical DRAM visibility. A genuine provider rebuild needs the producing C-SKY compiler/configuration. No physical clock, gain, microphone routing, interrupt timing or whole-component source completion is asserted. The earlier mistaken consumer check address is retained in FAILED-CHECK.md.

Existing completed behavior remains available in ../audio-notification-block-insertion-2026-10-09 (704 comparisons) and ../audio-codec-lifecycle-hal-composition-2026-10-09 (245 compositions). Their scheduler/peripheral fixture limits remain unchanged. Independently reviewed touch runtime source subtotal is now 1,074 bytes; eight array bytes and four CRT terminator bytes are separate data. These local results do not exhaust whole-firmware P2.
