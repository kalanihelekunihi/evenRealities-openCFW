# EM9305 source compile feasibility, bounded inventory

`receipt.json` pins the exact files, hashes, and tool availability observed for this pass. This is a separate ARCv2 EM / EM7D image lane. The existing `source_image` Python code builds the four-record deployment container from caller-supplied records; it does not build the controller application. Record 3 is 210,888 application bytes. No source-built EM9305 object, archive, record, or firmware image was produced here.

## Source-owned candidates and attribution

| Candidate | Retained source | Locked original evidence | Current status |
| --- | --- | --- | --- |
| `QEQueue_init` | Official QP/C v6.5.1 `src/qf/qf_qeq.c`, pinned commit `416dcec8820b9cdb5827497e645d0d9375db53c6` | Complete 24-byte `0x310f5c..0x310f74` body, SHA-256 `455385f66072cf7e1939132ba2f3716b5789a1b2a4ff64cef5a05afb5a302243`; field stores agree with source | Smallest executable oracle candidate; source semantics established statically, no ARC build/execution |
| `QK_sched_` | Official QP/C `src/qk/qk.c` | 56-byte `0x311634..0x31166c` body and downstream priority checks | Blocked at stock custom instruction `0x3d2f1000` at `0x31163e`, ARC port/config and IRQ state |
| SDK v4.2 named objects | Third-party historical SDK mirror at commit `e4412bc98d4e76d441d1226ca3696e53cfae5f54` | 40 exact named object/body matches in the locked payload, 18 v4.2 discriminators | Attribution evidence; four matches are data shaped and standard EM-Core source is absent |

The QP/C source is GPL-3.0-or-later or commercial licensed. The historical SDK mirror is a content-corroborated personal mirror, not an authenticated official source release. Its retained `compile.arg` and `compile_mw_for_em.arg` establish two different ARC core/feature profiles; neither is proved as the G2 producer profile. The registered v4.6 SDK has 238 C files and 109 prebuilt archives, but generic source or an archive match does not supply the missing G2 application configuration. The v4.2 retained mirror subset has no C file.

## Compile and data boundary

The required target is ARCv2 EM / EM7D with the EM9305 extension and SDK ABI. The documented SDK objects identify MetaWare T-2022.09 build 004, LLVM 14.0.6, `-Os`; that identity applies to matched SDK objects, not necessarily every vendor or application unit. `ccac`, `arac`, and ARC GCC/binutils assembler/linker were absent from PATH in this pass; local ARC **objdump** supports static decoding only. This host `clang` exposes no ARC backend. An ARM or host C build of QP/C would be a semantic model, not an EM9305 target object.

The complete product build also needs the producing ARC port (`qf_port.h`/`qk_port.h`), QP configuration including counter widths and assertion policy, custom APEX instruction definitions, EM-Core/Packetcraft controller source or licensed libraries, product callback/data definitions, exact linker script and initialized RAM map, MetaWare runtime/library and compiler options, and the four-record placement inputs. The standard EM-Core v4.2 mirror supplies binaries, symbols and headers, not its source. These are concrete source/data acquisition gates; no stock object bytes or executable arrays were copied into a candidate.

## Next executable oracle

`QEQueue_init` is the smallest bounded next step: obtain a qualified ARC compiler/runtime and an attributable EM9305 QP/C port/config, build `qf_qeq.c`, then compare stock and source public entries for zero and nonzero `qLen`, 255 overflow, ring pointer, initial head/tail preservation, and the 13-byte queue field prefix. The fixture must observe registers, memory writes, return state and any assertion path. Only after that oracle and source license review could this local unit be considered for an isolated source archive. The scheduler needs custom-instruction semantics and IRQ state separately. Neither unit would close the 210,888-byte application or its record packaging.

This pass changed no component source, selected archive, canonical gate, official blob, or shared ledger. Its completion is the finite feasibility inventory and identified next oracle; **zero** new BLE source units were admitted.
