# Stock transaction queue offsets and caller boundary

**Concrete stock queue-field layout found: +36/+40, with a blocking-mode reachability guard. No authenticated ordinary nonblocking entry was identified.** This is useful original-byte ABI evidence; it is not execution of a nonblocking transaction.

Locked main SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`; payload mapping `file offset = VA - 0x438000 + 32`. Four full original extents were hashed against both raw payload bytes and existing function census hashes. `stock-receipts.json` retains original hex, hashes, selected metadata and complete direct caller sets. `verify.py` independently checks 17 instruction byte receipts and decodes three Thumb BL targets.

| Fact | Original addresses and argument provenance |
|---|---|
| Validator transaction | Entry `0x55C1E0`: r5=r1 at `0x55C1E6`; r7=r2 at `0x55C1E8`. r1 is the transaction, r2 is blocking flag. |
| Queue guard | `0x55C25E` truncates r7 to byte; `0x55C260` compares zero; `0x55C262` branches to successful return at `0x55C280` if nonzero. |
| Pause field | `0x55C264` loads **byte** `[r5,#36]`; `0x55C268` tests reserved mask 0xE0. The byte optimization is sufficient for that mask; it does not make the source field a byte. |
| Status field | `0x55C272` loads **word** `[r5,#40]`; `0x55C274` loads mask from `0x55CC10`, original word `0x00E0E0E0`; the next TST rejects reserved bits. |
| Ordinary blocking caller | At `0x55CC62`, r2=1; `0x55CC64` r1=r4; `0x55CC66` r0=sl; BL `0x55CC68` reaches validator. r4 retains entry transaction r1. |
| Full-duplex blocking caller | At `0x55CF7A`, r2=1; `0x55CF7C` r1=r9; `0x55CF7E` r0 loads saved handle; BL `0x55CF80` reaches validator. r9 retains entry transaction r1. |
| Application transaction producer | Function `0x52DF50..0x52E058` exclusive retains wrapper in r4. Transaction base is sp+8. Stores at `0x52DFEE`/`0x52DFF2` zero sp+44/sp+48, thus transaction+36/+40. At `0x52E014`, r1=sp+8; `0x52E016`, r0=[r4,+4] (wrapper's HAL handle); BL `0x52E018` reaches full-duplex blocking `0x55CF40`. |

The caller also sets transaction direction byte at +20 to 2, byte count +16 to 2, TX pointer +24 to sp+4, RX pointer +28 to sp, and continue byte +32 to 0. It zero-initializes 48 bytes at sp+8, but **48 does not establish the queue offsets**: those follow from the separate original stores and validator loads. The initializer's semantics were not executed in this pass. Caller static provenance and original stores are sufficient to bind the supplied pointer/offsets; no source-only transaction is substituted.

Validator source order matches prior source: `if (!bBlocking)` then pause-mask and status-mask tests. The entire validator extent is 166 bytes and agrees with existing corpus hash `f0fa087eaffd371b53145fb705ff4cedc7974c95e955b3a89b051ce1bd64c408`. Both known direct callers pass blocking=1; therefore their paths skip the +36/+40 validator reads. The application caller does initialize those slots, but no actual queue consumer reached from a blocking=false caller is authenticated here.

## Three source candidates and ABI distinction

Registered `5efc0228528a8adce5eae0d226fac85d2551eb3b`: no FDNB API or mode field. Public `ef488e3b1fb1d612d61862595edd203ee9f6ca37`: TX DMA/RX IRQ FDNB API, no selectable eFdnbMode field. Supplied SDK 5.2: adds selectable RX DMA/TX IRQ and eFdnbMode before queue controls. The public source acquired by discovery is retained separately; its hash and its active-FDNB service prefix were checked locally without acquiring another checkout.

Under ordinary 4-byte enums/pointers and 8-byte uint64 alignment, old/public pause/status+36/+40 becomes SDK5.2+40/+44 while total stays48. Stock +36/+40 is compatible with old/public layout and excludes that conditional shifted SDK5.2 layout for this validator. It does not discriminate old from public by layout alone. With short enums the new eFdnbMode may fit padding at+35 and leave+36/+40 unchanged; exact producing options are missing. Stock uses a direction-byte load at+20, which does not independently prove the full enum allocation size. No total-size inference or admission of conditional layout as actual SDK ABI occurs.

The separately sealed service-dispatch analysis excludes the unchanged added active-FDNB dispatch in the selected stock service. Both public TX-DMA-only and SDK selectable implementations have that added active branch; the stock service enters bHP directly. This is a scoped control-flow exclusion of both unchanged newer service providers, not proof of whole-image API absence, whole SDK revision, or physical behavior.

## Exact search scope and stopping boundary

Read all 7,449 records in `g2/research/corpus/apollo-main/ghidra/decomp/functions.jsonl`, existing `g2/symbols/apollo_main.tsv`, relevant Ghidra bundle10 validator text, and the consolidated IOM prior analysis references. Inspected 25 function records in the address-bound IOM island `[0x55BCE8,0x55D280)` and selected source definitions in registered/SDK/public C/H. No named IOM/SPI nonblocking record appears. Metadata direct callers of validator are exactly `0x55CC1C` and `0x55CF40`; authenticated original BLs agree. Caller sets for the two blocking providers are retained in JSON. The existing main objdump listing corroborates the same two direct validator calls. Linear-disassembly matches are only corroboration, since data/code classification is not globally certified. No new all-image candidate sweep or generic partial-byte search was performed.

The symbol census labels much of this island Unverified. Selected extents and instructions were authenticated against raw bytes; inherited inferred names/signatures elsewhere are not promoted. This is not a closed callgraph: indirect calls, inlining, unrecognized functions and other payloads remain outside the scope. No claim that an ordinary/new nonblocking API is globally absent follows.

Missing input for the requested next execution stage: an authenticated nonblocking entry/caller setting blocking=false or a independently validated complete reachability boundary, plus exact producer enum/alignment/validation configuration and any retained FDNB state/dependencies. No synthetic fixture was executed. The finite static +36/+40 finding is complete despite this boundary.

Preservation checks passed: 3450 prior sealed entries under existing policy exclusions, 110 protected inputs, four checkpoints, unchanged index. No production/submodule-pin/device/Git mutation. Prior outputs remain sealed. Replay: `python3 g2/analysis/iom-queue-offset-stock-binding-20261009-implementation/verify.py`.

The independent review `../dependency-gap-audit-fresh-2026-10-09T192823Z/next-sdk-audit/FDNB-LINEAGE-INDEPENDENT-REVIEW.md` proposed 0x55CC1C..0x55CF2E as an unnamed ordinary-nonblocking candidate pending body/caller verification. This pass resolves it as ordinary **blocking** transfer: its authenticated 786-byte envelope has hash `119a1e56baf34bc9d36d5f3caa3fc27692d488d8fc65641c2d62518b8cc7ed01`, passes r2=1, saves/disables INTEN at 0x55CCE6..0x55CCF2, performs FIFO polling, then restores INTEN at 0x55CE2C. It has no CQ enqueue/callback parameter path. The finite candidate therefore does not supply a blocking=false caller. The identified stock SPI full-duplex provider and this ordinary blocking provider both consume the established transaction prefix without a selectable mode access. Source-derived role labels are bounded body interpretations, not linked symbol provenance.
