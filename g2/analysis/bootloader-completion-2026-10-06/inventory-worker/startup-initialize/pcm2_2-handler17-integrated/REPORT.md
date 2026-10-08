# Selector 17 integrated scatter-table successor

This is an isolated successor to the frozen record candidate, not a promotion.
The base copy is
`/tmp/opencfw-root-pcm22-relocated/handler17-integrated/frozen-record-candidate.elf`,
SHA-256 `4b1fb7505187310b0b9bcd84f1479693a313db9485d4741960a1fbdf6210c645`.
The successor ELF is
`/tmp/opencfw-root-pcm22-relocated/handler17-integrated/candidate17-integrated.elf`,
SHA-256 `687b0a4e3ce6aef856d19738977a8285033a36110c629d73b0b3cc7306da187d`.
The exact 202 frozen object inputs, source snapshots, and base-copy hash are
listed in `/tmp/opencfw-root-pcm22-relocated/handler17-integrated/input-manifest.json`
(SHA-256 `7e879f28ea2c71a28b1f3ea93abe4630856d9ef69e004c0830cdd8a544b11ab1`).
The copied record link recipe is retained here as `record-link.sh`; the staged
input copy recipe is `link-integrated.sh`, and the deterministic rebuild check
is `build-integrated.sh`.
Durable ignored copies of the candidate, base, verification receipt, original
manifest, and all 202 staged object inputs are stored in
`g2/build/bootloader-completion/startup-pcm22-handler17-integrated/687b0a4e3ce6aef856d19738977a8285033a36110c629d73b0b3cc7306da187d/`.
The adjacent `source/` directory keeps copies of the C, linker, and verification
inputs. `durable-input-manifest.json` remaps the staged paths within that tree
and has SHA-256 `b673245c517c9aa42493c7690f64a0988c9a98c59b95443ef3deee9a1074c127`.

The only reconstruction changes in the initialized record are compiler-owned
selector 17 pointer data and source-mask bitset `0x707c105`. The copied linker
script includes `pcm22_handler17.o` in the source segment. The isolated handler
receipt remains in the sibling `pcm2_2-handler17/` directory.

`/tmp/opencfw-root-pcm22-relocated/handler17-integrated/verification.json`
passes the bounded integration proof. A source-only machine executes the
successor's actual scatter adapter at `0x415326` (compiled source bytes
`49461df4deb9`) with installed record `[relative=4284, count=1250,
destination=0x20000000]`; its return `0x433110` matches stock. It loads no
official-image bytes. The resulting 1371 source bytes normalize to the stock
decoder output hash `e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843`,
and the untouched pad byte is `0xa5`. The installed selector 17 pointer is
`0x325a9`; the source-mask function returns `0x707c105`.

The same installed table drives the stock and source walker for the natural
9-to-10 transition. Both call selector 17 with `[10, 9, 3, 1]`, return
`[17, 1]`, and match ordered writes, output state, stack, and callee-saved
registers. This test does not rewrite the callback table after installation.
The receipt records 80/130 walker bytes, 160/390 selector bytes, and 258/310
handler bytes visited, with exact unvisited addresses. The seven-case integration
suite and unrelated startup regressions were intentionally not run for this
bounded successor.

## Follow-up validation on the frozen successor

The frozen ELF above was rechecked without changing its bytes. The actual scatter adapter installed
selector 17 at `0x325a9` and returned source mask `0x707c105`; after that installation, 14 direct
source calls were compared against the locked handler, including timer-enabled state paths. All
matched return registers, seeded state, ordered MMIO writes, wait cycles, callee-saved registers,
stack, and PRIMASK. The natural 9-to-10 walker comparison also passed using the same installed table
and arguments `[10, 9, 3, 1]`. The updated receipt is `validation/verification-direct14.json` in the
durable ignored candidate directory.

I reran the 1,400 initialized-state root comparisons with selector 17 included among native source
bindings. All 1,400 passed; no fixture was excluded, and the runner hash is
`e849466fb1716b03e5be0578ca3cf6991570e197bf4d4e383b6c47d73c59daba`. This is bounded comparison
evidence for the initialized-state family, not whole-firmware equivalence or promotion. The adapted
driver and receipt are under
`g2/build/bootloader-completion/startup-pcm22-handler17-integrated/687b0a4e3ce6aef856d19738977a8285033a36110c629d73b0b3cc7306da187d/validation/`;
`validation/addendum-manifest.json` records hashes for those artifacts. Its SHA-256 is
`d654141db96d4f1b4403d781181ebb330f43ccd251d26299c6a5a94a330d1fc0`.
