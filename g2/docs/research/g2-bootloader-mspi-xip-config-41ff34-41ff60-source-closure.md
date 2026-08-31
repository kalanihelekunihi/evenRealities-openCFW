# G2 bootloader MSPI XIP-config source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated entry `[0x0041FF34,0x0041FF60)` now routes to
`open_cfw_bootloader_mspi_xip_config_41ff34` in
`runtime_mspi_xip_config_41ff34.c`. The clean-room C preserves the observable
stock behavior: it truncates the argument to eight bits, writes `8` to byte
five of the retained configuration object at `0x2000023C` only when that byte
equals one, otherwise writes zero, then always calls the retained MSPI control
entry at `0x004251C0` with handle word `0x200270DC`, request `16`, and the
configuration address. The retained return status is intentionally ignored.

The 44-byte stock body has SHA-256
`384a53a67910d2378b5f063ef45d4521d16c91098921a933f7a4a1d679eabe76`.
Its three direct callers are `0x004203B0`, `0x00420ED6`, and `0x00420F36`.
The literals at file offsets `0x10A04` and `0x10874` authenticate the
configuration and handle addresses. Request `16` corresponds to the Ambiq
MSPI XIP-config request, but the source documents only the observed byte-level
mutation and call contract rather than assigning an unverified structure-field
name.

Host tests pin both low-byte branches, truncation, write-before-call ordering,
the exact handle/request/config arguments, and ignored status. Apple Clang and
Linux Clang both emit the same relocation-free 36-byte leaf with SHA-256
`0cc0ac059e80451afec8ddbad56203612ebc34a9559a549f6c499bd958be87eb`.
The 1,939-byte source file hashes to
`5f5bea367de55e637c87bc3e5888a7350654692af1499a3bd5b45ace2c3a6d8e`.

The later bit-run helper pair is now source-owned as well. The cumulative
Apple overlay/provider are 10,642 / 159,242 bytes with SHA-256
`7de98b3896cc3267d44e696711fadde0772ca8bf4394985ee0b39839063e1ff8`
and `abadb47cadb948f7c7037375473ea044a69ca76e9e7ea27769e5109367fcbda4`.
Linux identities are 10,610 / 159,210 bytes with SHA-256
`7f43e5bc46e5bcf198d49d28d796c5ed64c1bcb15043c715c629cae2f1736867`
and `8a099f30ccd0c05af8dcaa28dd4301b01e04526bcbce57866a59f21b780b7662`.
Accounting is 10,629 source-owned, 11,944 generated patch, 14 alignment, and
136,655 retained official bytes across 172 functions, 153 relocated leaves,
and 170 patch sites. Apple headroom is 4,598 bytes.

Unsigned Apple/Linux packages are 4,740,820 / 4,516,798 bytes with SHA-256
`c8ebec84cc96fd07030be9bf632061263248bcf775ce46eadc04a1211e8e948f`
and `51439e677eb68babc0d54fb211cbe120c5a5b3a641855a940979977a42607af7`.
Their flash plans are 4,517,526 / 2,406,772 bytes with SHA-256
`cfbaa67130d3307c1cd50a471d0873f499e7df8251ec333c37c8c26de538e197`
and `6cc11e3f306cf4b777ccdf80cd8a8f04fd604e89cfb2ac92eb12e3128aabfe2e`.
They contain 6,494 / 3,448 placed regions, two unresolved address regions,
five container-only regions, and six protected regions.

No signing, flashing, installation, reset, boot, MSPI mutation, or other
hardware operation was performed. Live XIP transition, timing, external-flash,
and cold-boot behavior is explicitly blocked by unavailable physical evidence:
there is no authorized responsive right G2 temple and the left temple must
remain stock. Executable bodies after `0x00420002` remain software gaps, so
firmware-wide functional completeness is not claimed.
