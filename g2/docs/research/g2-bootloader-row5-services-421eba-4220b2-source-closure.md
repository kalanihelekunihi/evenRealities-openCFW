# G2 bootloader row-five client-service source closure

The complete authenticated two-function cluster at
`[0x00421EBA,0x004220B2)` now compiles from maintained clean-room C at its
exact stock addresses. Apple clang 21 and Homebrew clang 22.1.8 reproduce all
504 installed bytes exactly.

The enable transaction maintains row-five client membership under critical
sections, refreshes a 50-tick published timeout for existing clients, and
coordinates selector client `0x36` with the mode-zero or mode-one service.
First-client setup arms the pending byte, invokes the retained dual switch and
commit providers, publishes active/state cells, and rolls bitmap, selector and
switch state back on failures. The disable transaction is idempotent, removes
the low-byte-selected client, and on the last client invokes retained null
commit, releases both selector modes, clears pending/active/state cells and
turns the retained dual service off.

`runtime_row5_services_421eba.c` is 12,657 bytes with SHA-256
`4b70866962150221eb8d3b1a3527f70d431f3fda19bce500fceed9ae95b92ebf`.
The installed 390-byte enable body has SHA-256
`5d5e8bce49145dfddb318e0aff9baf61150e00e95f6fc7c804fde126dd11f68c`
and unrelocated SHA-256
`1115cefffbaeab2975dc13443a6e983f66bdd66d83e9d6553e75a89e3b3c1ef1`.
The installed 114-byte disable body has SHA-256
`fa335e0a8bf71ef86975470840768672bd90ad0eaac982abfc68e8c84de0bd17`
and unrelocated SHA-256
`c67158c2415dff61e9c1a4bf1a4145191e784a59c6dd426bb5eff16c14a21203`.
Twenty-six strict calls bind source-owned bitmap, critical, mode-selector and
cleanup services plus retained dual switch/commit/null-commit providers.
Seven focused tests pin both bodies, literal cells and the `0xE92D41FC`
successor; exercise existing-client refresh, first-client commit/activation,
mode-enable and commit rollback, absent/nonfinal/final disable; and compile
both reviewed profiles.

Canonical accounting becomes 18,463 source-owned, 16,528 generated patch, 16
alignment, and 128,833 retained official bytes, including 362 cave bytes and
2,876 exact in-place bytes across 229 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,591,243-byte flash plan has SHA-256
`442828e94f28cfddc078420b99a16ae9a8a8cb888a1dcc09885b95ff9fe1c93f`
with 6,597 placed, two unresolved, five container-only and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but live interrupt timing, retained dual-provider behavior, shared
bitmap/state ownership, mode-selector coordination and physical row-five
effects require authorized hardware evidence. That evidence is unavailable
because no authorized responsive right temple exists and the left temple must
remain stock. Firmware-wide functional completeness is not claimed; the next
retained executable body begins at `0x004220B2`.
