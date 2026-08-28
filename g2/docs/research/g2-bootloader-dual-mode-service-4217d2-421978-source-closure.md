# G2 bootloader dual-mode transaction service source closure

The complete authenticated service at `[0x004217D2,0x00421978)` now compiles
from maintained clean-room C at its exact stock address. Apple clang 21 and
Homebrew clang 22.1.8 reproduce all 422 installed bytes exactly.

The service accepts null, `0x0EE6B280`, or `0x0BB80000` instances and rejects
other instances with status 5. For a null configuration it selects controller
zero or one from the current mode byte, requires the selected controller or
returns status 7, and queries the retained provider into a local copy of the
authenticated `{0x00020000,0x000C49BA,0}` template. Query failure returns
before entering the critical section.

The transaction saves interrupt state, queries source-owned bitmap row 5,
and applies the stock busy/idle compatibility policy. It preserves distinct
mode-zero and mode-one enable/disable paths, the fixed commit/null-commit
providers, paired critical-mask restoration, failure cleanup through both
disable paths, 12-byte configuration publication at `0x20026FF8`, current
instance publication at `0x20027034`, and readiness byte `0x20000551`.

`runtime_dual_mode_service_4217d2.c` is 11,348 bytes with SHA-256
`5bce18dd5696d3f85f6bbb98661d63bd519368727ffc8b184db36276c7a1192f`.
Its 16 reviewed `R_ARM_THM_CALL` relocations bind query, critical-save,
source-owned bitmap count and copy, mode-zero/mode-one enable and disable,
and commit providers. The unrelocated body SHA-256 is
`8989f172e6dd5e8b678f92ef0a6131f25b9ad817f6356aa5aaf304256cca4726`;
the installed stock SHA-256 is
`05c24e9854dcc0df94616fd1bbfd81f540add09f4e915b0ebfd998b2052e12f7`.
Eight focused tests pin the body, literals, dispatcher caller and successor;
exercise invalid and missing controllers, both query routes, query failure,
busy incompatibility, successful transition/commit, failure cleanup; and
compile with both reviewed Cortex-M55 toolchains.

Canonical accounting becomes 16,613 source-owned, 16,528 generated patch, 16
alignment, and 130,683 retained official bytes, including 362 cave bytes and
1,026 exact in-place bytes across 213 source-owned functions and 201 patch
sites. Apple/Linux providers remain 163,840 /
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`
and 163,824 /
`d0a97870b861c089e4ac029ba1c7a1c0cc67d6112c3416a5cda657a038c3a8ea`;
unsigned packages remain 4,745,418 /
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`
and 4,521,412 /
`9438fb68b25110b5c03309e868e5baa78e6989a88c3597d939ef7017ef28543e`.
The 4,579,844-byte flash plan has SHA-256
`2a34cd666945adc7929451a5b56bc7432b0519a7419f4c47bc8c24da0a5aff1e`
with 6,581 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but interrupt timing, controller/register behavior, shared-state
ownership, and physical mode transitions require authorized hardware
evidence. That evidence is unavailable because no authorized responsive
right temple exists and the left temple must remain stock. Firmware-wide
functional completeness is not claimed; the next retained executable body
begins at `0x00421978`.
