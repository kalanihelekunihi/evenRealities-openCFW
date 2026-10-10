# Bounded TLSF control layout and search automation

Status: ready for independent review. The previously Unverified 48-byte body at `0x004D0524–0x004D0554` is behaviorally attributable to TLSF `control_construct`. The related 120-byte `0x004CFFC2–0x004D003A` agrees with `search_suitable_block` on valid allocator states, and its inconsistent-bitmap assertion arguments match the pinned source expression and line. This adds a concrete allocator control layout beyond the prior mapping geometry pass. It does not establish whole allocator correctness, a unique producing revision, compiler identity or campaign acceptance.

## Authentication and private scope

Read the current workflow README, PROCEDURE, CONTRACTS and REPOSITORY. Original Apollo main SHA-256 is `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`; body hashes are independently recorded at `g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl:3418,3433`. The original payload offset is runtime address minus `0x00437FE0`. `probe.py` verifies full input and both body hashes, authenticates the earlier analysis ELF's PT_LOAD address, size and complete original mapped bytes, and copies it to this private directory. Authored ELF metadata supplies Thumb analysis context; it is not original build evidence or whole-image code classification.

Source comparator is the retained pinned TLSF source at `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/tlsf/tlsf.c`, SHA-256 `2a0f8cfc9cfe6114ccdc6cf22339059440b16f1149b5107bead4ae4c3a0d50e2`. Relevant source spans are `345–357` (control structure), `543–574` (search) and `797–814` (initialization). No dependency download was needed because the existing authenticated comparator suffices.

## New source-backed layout

Both independently decoded bodies establish these offsets relative to the control pointer:

| Field | Offset / size |
| --- | --- |
| sentinel block | `+0`, 16 bytes |
| sentinel next_free / prev_free | `+8`, `+12`, 32-bit pointers |
| first-level bitmap | `+16`, 32-bit |
| second-level bitmaps | `+20`, 24 32-bit words |
| free-list heads | `+116`, 24 rows of 32 32-bit pointers; row stride 128 |
| end of last field | `+3188` |

Initialization writes exactly 795 words: two sentinel pointers, one first bitmap, 24 second bitmaps and 768 heads. Sentinel pointers and every head receive the control address; all bitmaps receive zero. The first eight bytes and bytes at/after `+3188` retain their prior values. This is faithful partial initialization, not an assumed full structure memset. The source declaration explains the untouched sentinel physical-prev/size fields; their runtime meaning is not inferred solely from this initializer.

Search masks the current row by `~0u << sl`. If nonzero, it selects the least set second-level bit. Otherwise it masks the first-level bitmap by `~0u << (fl+1)`, returns zero if empty, or selects its least set bit and writes the new first index. It then chooses the least second-level bit, updates the second index and reads the head at `control+116+128*fl+4*sl`. On exhaustion it leaves both index outputs unchanged. Control memory is read-only on these paths.

Under an inconsistent state where the first bitmap advertises a later row but that row's second bitmap is empty, stock invokes provider `0x004D09B4` with expression `sl_map && "internal error - second level bitmap is null"`, file `D:\01_workspace\s200_ap510b_iar_git\third_party\tlsf\tlsf.c`, and line 568. That expression and line agree with the comparator. This strengthens source-family attribution but does not uniquely identify a revision. Execution stops at the provider; whether it returns, halts, logs or resets remains external to this bounded result. Raw Ghidra's apparent continuation after that call is not an established provider contract.

## Tool automation and independent evidence

Ablation at pin `97e051b44d1ac8129b35556fe533e6e8b5338db2` profiles both original-byte bodies with explicit Thumb state. The initializer has no calls; search yields three call sites: `0x004CFFFA → 0x004CFD56`, `0x004D001A → 0x004D09B4`, `0x004D0024 → 0x004CFD56`. GNU force-Thumb listing independently agrees. The two calls to the same least-set-bit helper and the assertion branch are retained separately rather than collapsed into a two-callee count.

Private Ghidra 12.1.4 import uses bounded disassembly only, with `TMode=1`, no whole-image analysis, and complete bodies identical to the historical extents. `BoundedTlsf.java` preserves raw exports; `run_ghidra.py` preserves actual command, log, language/compiler/SLA hashes and output hashes. ELF import chooses `ARM:LE:32:v8:default`, an analysis setting rather than a claim about hardware. GNU and Unicorn independently corroborate the exercised Thumb instructions. The private project makes a future dedicated Ghidra-MCP attachment possible; the existing unrelated bridge instance was not touched. Its query transport adds no independent semantics here, so headless export suffices.

Raw Ghidra still uses integer control pointers and untyped return values, but its field arithmetic and bounded loops agree with the source and original-byte checks. Adding source-derived types could improve presentation; it would not create additional behavioral evidence. REA's ARM ELF admission and Ghidra orchestration similarly add transport convenience without a new execution oracle. Prior tool capability reports already resolve those architectural limits, so no generic REA rerun or global tool setting change is justified.

Unicorn 2.1.4 executes the original initializer, original search routine and original real bit helpers. The 2,672 search cases cover all 768 bins with exact-hit and empty states, next-first-row transitions for every non-final row/bin, and 400 deterministic bitmap samples. Every result, both index outputs, stack restoration and absence of control writes matches source-derived expectations. Initialization verifies all 795 write addresses/sizes/values and untouched bytes. The separate assertion probe verifies actual arguments and stops before executing its provider. `receipt.json` retains deterministic case hash, observed addresses, original input hashes and all results. This is bounded evidence on valid indices/states, not full-domain proof for invalid indices or full allocator execution.

## Replay and stopping boundary

Run `/Users/kalani/Repos/ablation/.venv/bin/python g2/analysis/shortcut-tool-automation-20261009-agent2/probe.py` for authentication, profiles, GNU listings and original-byte execution. The private Ghidra project is already created; run `python3 g2/analysis/shortcut-tool-automation-20261009-agent2/run_ghidra.py` to replay exports and receipts. The initial project was created using the same private ELF, `-import`, `-noanalysis`, `-scriptPath` and `-postScript` options recorded in the exporter script. Project/ELF outputs are ignored analysis artifacts; scripts, raw exports and receipts are retained.

The useful shortcut is reusable bounded authentication → call triage → GNU comparison → original-byte execution → raw private decompilation. Tools speed enumeration/export, while the new accepted candidate facts depend on the original instructions and comparator. Further generic dependency searches cannot settle the assertion provider or other allocator bodies. Those require their own bounded P2 review scope. No canonical files, gate records, firmware sources, existing projects or submodule pins changed; no classifier denial occurred.
