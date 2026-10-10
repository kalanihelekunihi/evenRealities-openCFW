# Touch newlib constructor walker: new finite provider match

**Unmodified pinned newlib source regenerates all 72 stock bytes after the five independently bound relocations.** Installed Arm14.2 nano libc matches the same complete extent; regular libc differs. This closes the previously untested constructor-walker provider comparison, not full startup composition or unique producing toolchain identity.

## Selection and hypothesis

The repository's `source-dependency-next-ledger-2026-10-09/REPORT.md` explicitly marked libc constructor walker0xA9E4 untested. The SDK5.2 source/archive inventory supplies no authentic IAR DLIB/runtime archive; its available HAL/CMSIS/crypto archives do not provide a target-bound new runtime test. Existing registered/locked touch GCC/newlib provenance supplies a concrete 56-byte function with independent instruction hash, installed nano/regular objects and a source revision selected earlier from official Arm14.2 metadata. This made constructor order and complete linked bytes a higher-confidence test than unanchored middleware attribution. No DSP/LZ4/Nema/audio/STRDIS/FDNB/queue test was repeated. No extra agent was started.

Hypothesis declared before compilation: stock constructor walks preinit, calls _init, then walks init, consistent with the known newlib source/provider. Candidate source revision `7923059bff6c120c6fb74b63c7553ea345c0a8f3` was inherited from authenticated Arm release metadata, not chosen by byte fitting. Exact `newlib/libc/misc/init.c` was acquired with its CodeSourcery permissive notice; URL/hash in acquisition.json. It was not modified.

## Original binding and complete comparison

Locked touch payload 34464 bytes, SHA-256 `0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`. Strip its32-byte FWPK header; image base0x3300, so payload offset=VA-0x3300+32. Code `[0xA9E4,0xAA1C)` is56bytes/hash`af3f65a359e82cdfb692ebd2ae063f2a27b25dd3d90365d05624aaa7d319ef27`; four literal words occupy `[0xAA1C,0xAA2C)`,16bytes. Full72byte extent hash`658aa248574049c50b246ca9a858759a02660b57667b39bede014d5e978df7e7`.

| Binding | Original evidence |
|---|---|
| preinit end | LDR at0xA9E8 → literal0xAA1C →0x2000087C |
| preinit start | LDR at0xA9EA → literal0xAA20 →0x2000087C |
| _init | BL at0xA9F6 independently decodes target0xAA44 |
| init end | LDR at0xA9FA → literal0xAA24 →0x20000880 |
| init start | LDR at0xA9FC → literal0xAA28 →0x2000087C |

Thus preinit count0, init count1 for these bounds, using4byte function pointers. Array addresses are RAM, not copied constructor target values. Neither the current RAM contents nor reset initialization of that array was executed or inferred. Real _init code `[0xAA44,0xAA50)` is separately receipted: push, NOP, balanced register pops, restore LR and BX LR. It was not replaced by a handwritten stub. The linker receives its original Thumb address0xAA45 as an external binding; no callback code is supplied in comparison output.

Both nano and regular `libc_a-init.o` were extracted from existing authenticated toolchain archives; archive/member hashes are in archive-identities.json. Nano has exact executable instruction layout and relocation closure: THM_CALL at+0x12 to_init; ABS32 at+0x38/+0x3C/+0x40/+0x44 to the four arrays. bind.ld uses only the separately decoded target/literal addresses. No masked relocations, discarded function tails or manually patched bytes enter the equality claim. Object-disassembly records name each relocation.

Results:

- Nano object linked extent72bytes exactly equals all stock code+literals.
- Regular libc linked extent72bytes differs, hash`7eede674c70893eed7d24cf974e5076d09681498e5bebe72b9384e244837e234`.
- Source compilation with installed application headers initially omitted `_HAVE_INIT_FINI`; linked extent68bytes differs. Installed newlib.h supplies `_HAVE_INITFINI_ARRAY` but not that internal runtime configure macro.
- A single evidence-directed compilation with `_HAVE_INIT_FINI=1` produces exact72byte equality. Basis is the original _init BL and nano object relocation plus the source's explicit conditional call. Flags: Cortex-M0+/Thumb,-Os,function/data sections,nano.specs. Source itself unchanged. This is a genuine source/provider discriminator, not recovery of all vendor libc configure flags.

The compiler ran in the already installed network-disabled unprivileged container, read-only toolchain mount and owned output mount. Initial sandbox DNS and Docker-socket restrictions were recovered by permitted narrow operations; receipts retain failure and successful commands. No firmware/device execution occurred. Comparator ELF/object/binary outputs are isolated analysis artifacts, not admitted firmware sources or a retained executable replacement. verify.py independently checks original hash/extents/literals/BL, both positive complete-byte matches and two differing controls.

## Boundaries and preservation

No constructor callback target, main startup integration, init-array copy source, _init source/compiler provenance, fini/exit wrapper, exact whole runtime build recipe, physical execution or source-complete/byte-identical firmware claim follows. Regular/nano object distinction and evidence-directed source feature match do not uniquely date the original GCC/newlib producer: other revisions/configurations may emit the same code. Tools-and-selected-config.json hashes compiler/cc1 and selected config, not all transitive generated headers.

Prior evidence preservation was independently checked:3455 sealed entries under existing policy exclusions,110 protected inputs and four checkpoints match. Index is stable during this verification, but differs from the prior track's index sample; this track performed no index operation and does not attribute the external difference. No production/submodule-pin/shared-campaign/device/commit/push mutation. No relevant local skill applies to this code/static comparison.

Deliverables: stock-receipts.json, comparison.json, acquisition.json, build receipts, original/nano disassemblies, tools/config identities and verification.json. Recheck with `python3 g2/analysis/touch-newlib-init-array-discriminator-20261009-implementation/verify.py`.

The newly communicated stock-versus-SDK5.2 delay-adjustment lead remains a separate unexecuted candidate; this constructor source/provider test was already underway and is complete. It is not folded into this extent or result.
