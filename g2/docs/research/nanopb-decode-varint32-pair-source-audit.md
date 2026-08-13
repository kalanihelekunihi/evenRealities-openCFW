# nanopb `pb_decode_varint32_eof` / `pb_decode_varint32` production-source audit

## Result and boundary

The production translation unit
`components/shared/nanopb/runtime_nanopb_decode_varint32.c` adapts nanopb's
private EOF-aware 32-bit decoder and public wrapper as two independently
auditable source leaves. It uses the shared recovered stream ABI and calls the
source-owned `open_cfw_nanopb_readbyte` seam. Each stock entry has its own
bounded patch, and the private text/literal closure and public text have
independent manifest ownership.

This is an offline compatibility promotion. No signing, flashing, reset, boot,
or hardware operation is part of this work.

## Authority and stock mapping

The selected authority is authenticated nanopb 0.4.9 tag `nanopb-0.4.9`,
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. The canonical brace-balanced
upstream definitions are 1,721 and 132 bytes. Their SHA-256 values are
`66833ae2defb892aa17162625ef107bda03be44e73f0b120d48e6d2b52770e2c`
and `ef3f2bd19c12b07ca055ab63f8e82ea6f4b34e67aefb277435092e7485834f0f`.
This compatibility selection is **not proof** of the vendor's historical
point release or of the absence of a vendor backport.

The authenticated stock private body occupies `[0x0048F4B8,0x0048F5AE)`
and the adjacent public wrapper occupies `[0x0048F5AE,0x0048F5B8)`. Their
respective stock hashes are `8583fa17383d72bbdcab6c2a7a20369dc0598d3ac3061feaf8a7b29dfa520150`
and `48218a658cffd7aeddfb623c9d0e7bd038ceb2a6898e9f8d08b10d5779f4f79b`.
Whole-image branch and stored-pointer scans close ingress to the two entries;
the private leaf has two calls to `pb_readbyte`, while the public wrapper calls
only the private provider.

## Behavioral qualification

The host differential oracle includes pristine authenticated `pb_decode.c`
once and wraps its file-static EOF-aware decoder without altering `static` or
pasting a second implementation. Production private/public results are compared
with pristine private/public results for destination-on-success, EOF signaling,
remaining budget, callback position/count, consumed bytes, and exact sticky
error classification. The deterministic corpus covers all one-byte values,
32-bit boundaries, every fifth-byte pattern, zero and negative extensions,
the 63/64-bit extension guards, every truncation/budget/failure position,
callback budget mutation, and hand-written expected outcomes.

## Deterministic target closure

Apple Clang 21.0.0 object, function-section, alignment, relocation, read-only
literal, and unwind pins are executable test constants in
`tests/test_runtime_nanopb_decode_varint32_production.py`. The production object
is built twice. It owns one 16-byte read-only `"varint overflow"` closure,
allocates no writable data, exposes only the explicit source-to-source readbyte
dependency, and keeps both functions in distinct sections. CANTUNWIND metadata
is authenticated and deliberately excluded from the installed closure.

The current Apple production object and extracted closure are:

| Item | Bytes | SHA-256 / alignment |
|---|---:|---|
| Complete object | 1,628 | `626893ac400caac8fa733f5740b272d218a1e32572fad4bfa636a4bce142c166` |
| Private text | 222 | `5296b608c55171bca9d5f4d162cf53d0e6aa5f724e1cb82499a7311f2a6cc9ff` / 4 |
| Public text | 10 | `e9ec8b612503f867aabf2467e3abfac44753c5576a247a00cbc4309e2a023f93` / 4 |
| Overflow rodata | 16 | `e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d` / 1 |
| Each function's exidx | 8 | `01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d` / 4 |

The private text relocations are two `R_ARM_THM_CALL` records at `+0x10` and
`+0x6A` to `open_cfw_nanopb_readbyte`, followed by the local literal's
`R_ARM_THM_MOVW_PREL_NC` / `R_ARM_THM_MOVT_PREL` pair at `+0xD0` / `+0xD4`.
The public text has exactly one `R_ARM_THM_CALL` at `+0x04` to the private
source-owned symbol. Each exidx section contains `0000000001000000` and one
`R_ARM_PREL31` relocation to its own function section. Both reviewed compilers report the
entries as `CANTUNWIND`; there are no personality routines, exception table
sections, extra relocations, unintended undefined runtime symbols, or allocated
writable sections. Linux negative mutations independently reject personality/data,
cross-function, and extra-relocation companions, plus an injected writable section.

Source, verification, vendor snapshot, adjacent nanopb, and before/after
artifact checks first confirmed that qualification did not alter production
output. The later production promotion preserves the independently audited
stock boundaries and dependency closure above.

No homolog of either decoder entry was found in the authenticated bootloader.
The selected nanopb 0.4.9 source remains a compatibility baseline inside the
source-equivalent 0.4.7--0.4.9 range, not proof of Even Realities' historical
nanopb point release or checkout.

## Installed Apple ownership

The private stock entry is replaced by a 246-byte generated patch at file
offset 357,592 / runtime `0x0048F4B8`, SHA-256
`39cbc613617df123fca8a706d6d8664f110ed5075f6586ade5947db3d7ea6450`.
Two zero bytes align the 222-byte private text at component offset 3,648,368 /
runtime `0x007B2B50`; its 16-byte literal follows at `0x007B2C2E`. A separate
two-byte alignment precedes the 10-byte public text at component offset
3,648,608 / runtime `0x007B2C40`. The public 10-byte stock entry at file offset
357,838 / runtime `0x0048F5AE` is independently patched, SHA-256
`d9ece4c36d9d25d448b14b93d09176014efb56468d4c4570be54a232522a04aa`.

The 957-region Apollo-main manifest owns the two patches, both alignment
regions, private text, private rodata, and public text independently. The
package flash plan has 1,029 programmed, two preserved, and five skipped
regions. Current effective package ownership is 125,994 source-owned bytes,
88,625 generated bytes, and 4,212,493 opaque bytes.

The current Apple production artifacts are:

| Production artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 125,222 | `a21779625714a5c029652287e38939ac4290306b3a8781045501839d385a1c62` |
| Apollo-main component | 3,648,618 | `99b1718f989695a4fe39655e8cf31ea7ef19ce97ed96b70fc1796c847bd2dead` |
| Core-source package | 4,427,112 | `92d1d9a2f2d80b503b2b68d1533a1c990da5a215381a0a22b604e63b6f7fb229` |
| Canonical build report | 2,323 | `eb0c87492532f136569cb529b2202805bd8bd84a45f76e0538b4ec1822bfe1b7` |
| Canonical flash plan | 738,871 | `1ee4d8d5a21a2b0d79173c5b78bcdf752407ae0e26d086ea5c5df4b504c939d9` |

## Installed exact-root Linux ownership

The independently recorded replay uses the reviewed source spelling
`/Users/kalani/Repo/SybilSightABCD/openCFW` and
`/home/linuxbrew/.linuxbrew/bin/clang`, exactly `Homebrew clang version 22.1.8`.
Two complete recompilations produced identical 1,628-byte objects, SHA-256
`626893ac400caac8fa733f5740b272d218a1e32572fad4bfa636a4bce142c166`.
The private/public text, literal, relocations, and both eight-byte CANTUNWIND
companions are byte-identical to the independently pinned object sections above.

Two alignment bytes place the 222-byte private text at overlay offset 126,796 /
runtime `0x007B3270`; its 16-byte literal is at overlay offset 127,018 / runtime
`0x007B334E`. Two more alignment bytes place the public 10-byte leaf at offset
127,036 / runtime `0x007B3360`. The Linux entry-patch hashes are
`1f64403d69443c2467c739594a66bd4f251ab9ad13cd55a2e6a42cb147788eba`
and `7f1122db2b85b3c028dbe0c818caa26e7fee00d0e772f9ae423e369ec1d49309`.
The final overlay ends at offset 127,046.

| Exact-root Linux artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 127,046 | `593833cbe89b7f195f97d0e9bef8b57c98c4efe4b7cf13a035b4604738c38364` |
| Apollo-main component/provider | 3,650,442 | `2712b0ca1feef4e75cb25c0d619814273d06d4aa82fbe85feb29dd874107c5ef` |
| Core-source package | 4,428,936 | `2a3c7b0298f3dcd52dc05fc3b0cbcf0bd3e282daa9c3b93ba47e4deff442865b` |
| Component build report | 1,540,536 | `37f414b756c38766a2894dde6174efdb9ed174a8253071963d57c032b42f3592` |
| Package build report | 2,322 | `e79568709dcd979a2a06ed986b8fcc0d717bca88772e82e67d91ba4a475d048d` |
| Flash plan | 604,887 | `de21f80249bcfda259e017512b8b25ba9e07437926cbe05d1e8e558f1177f424` |

The canonical manifest still contains 957 independently tiled Apollo regions;
the noncanonical profile coarsens the appended source tail, so its effective
flash plan has 847 placed, two unresolved, and five container-only regions.
Effective package ownership is 127,927 source-owned, 88,516 generated, and
4,212,493 opaque bytes. No package was signed or flashed, and no G2 hardware
was reset, booted, or otherwise operated.

`./make.sh verify`, `make vendor-snapshots`, and adjacent nanopb
production/snapshot suites authenticate those current outputs. The earlier
candidate-only no-output-change result remains historical qualification
evidence, not the current production artifact claim.
