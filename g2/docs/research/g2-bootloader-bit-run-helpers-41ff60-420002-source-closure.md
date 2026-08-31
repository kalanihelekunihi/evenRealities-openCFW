# G2 bootloader bit-run helper source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated helper pair `[0x0041FF60,0x00420002)` now routes to
two production functions in `runtime_bit_run_helpers_41ff60.c`. The first
loads one 32-bit word and repeatedly evaluates `value &= value << 1` until
zero, returning the longest consecutive-one run length. The second scans the
same word from bit zero through bit 31, selects the first strictly longest run,
computes the stock midpoint-biased index, and preserves the observed bit-one,
bit-30, parity, and terminal-run adjustments. The address-derived names avoid
claiming an unverified hardware-field meaning.

| Entry | Stock bytes | SHA-256 | Direct caller |
| --- | ---: | --- | --- |
| longest-one run `[0x0041FF60,0x0041FF74)` | 20 | `93e9d3dc1df2d950f6d5c0bae26e198c166b5388c3a4a69f9999715358fc4ad2` | `0x004200BE` |
| longest-one center `[0x0041FF74,0x00420002)` | 142 | `3c89f5f441c8c6b0163697b7eb6f2bafe5a4ff6092b294191a5200ae6fa679ed` | `0x00420158` |

Host tests pin the exact scalar translation across boundary patterns and 2,048
deterministic random words, in addition to both stock spans and their sole
callers. Apple Clang emits relocation-free 16- and 126-byte leaves with
SHA-256 `a690bd1df07a26fa65416653fee80c088615b3c492786331ee08f1446585ef4d`
and `d36402e8d02ee3663653477b656cd3ba1b713dc65688373e34f3d20332926390`.
Linux Clang emits the same 16-byte run-length leaf and a 110-byte center leaf
with SHA-256
`bd289ba0cbbb817f97d9fcb9b49b12fb9bc592426a1b0cbf4fba24d9d369ae63`.
The 1,898-byte source hashes to
`4647db644148f4df98454c6018d684a70e52306b0f2cfbbdfd79749fd2f53903`.

The cumulative Apple overlay/provider are 10,642 / 159,242 bytes with SHA-256
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
hardware operation was performed. Live training-mask meaning, timing,
external-flash, and cold-boot behavior remains blocked by unavailable physical
evidence: there is no authorized responsive right G2 temple and the left
temple must remain stock. Executable bodies after `0x00420002` remain software
gaps, so firmware-wide functional completeness is not claimed.
