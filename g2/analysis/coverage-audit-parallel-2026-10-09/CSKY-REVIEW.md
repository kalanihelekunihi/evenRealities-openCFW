# Independent C-SKY indexed-word accessor review

Decision: bounded static interpretation supported; ready for coordinator consideration after campaign contract/provenance records are supplied. This is not campaign admission or a gate receipt. No packet, task or campaign state was edited.

## Independent byte and mapping verification

[CSKY-VERIFICATION.json](CSKY-VERIFICATION.json) records a fresh repository-only hash/byte check, without rerunning the author's verifier or invoking its disassembler. All packet DELIVERABLES entries match. The child and official codec payload match the packet's SHA-256 pins. The complete child occurs exactly once in the payload, at `0xC590`. The body at child `[0x28B0,0x28C0)` matches payload `[0xEE40,0xEE50)` and SHA-256 `6bdb07c6468e4e2d97ba7c22736df347e8f2736c8d5009f053d8958265bceb3c`. Conditional base `0x10203004` maps this to `[0x102058B4,0x102058C4)`.

The stored [body disassembly](../csky-indexed-word-accessor-2026-10-09/body.objdump.txt) tiles 16 bytes with six 16-bit instructions and one 32-bit BSR. Push/pop preserve r4 and link; shift forms the word index; r2 is saved in r4 before calling the direct load helper; the returned r0 word is stored through r4. The helper bytes `00903c78` at child `[0x25E8,0x25EC)` agree with the existing full-XIP `ld.w r0,(r0,0); jmp r15` decode. Adjacent body at `0x102058C4` is excluded.

This supports the packet's 32-bit wrap arithmetic, one helper load and one output store, without bounds checks. Fault/access behavior remains conditional on actual mapping. The four Python semantic fixtures are examples of the stated model, not original-instruction execution or independent semantic validation; the packet labels them correctly. Aliasing is load-before-store. Unknown device identity, live base ownership and higher-level purpose are correctly left unresolved rather than guessed.

## Caller claim

The existing full-XIP disassembly at `0x10205B20–0x10205B2A` loads r4 with `0x20027350`, copies current r14 to r2, sets r1=2, loads r0 from r4+`0x5CC`, then directly calls this entry. `0x10205B48` reloads stack offset zero. The reported caller setup is supported. The intervening calls at `0x10205B34` and `0x10205B3E` preclude inferring uninterrupted output lifetime or absence of aliasing without their contracts.

The single direct-BSR census describes the stored complete-XIP decode, not global reachability: indirect calls, alternate mappings, other images, or data decoded as instructions remain outside that count. For durable admission, hash-pin the consumed `full-xip.objdump.txt` and its decoder provenance in the new packet's direct-input records. Its current results pin image/tool but do not hash that consumed caller-census file.

## Ownership and admission requirements

The 117-task scan applies a regex only to each task's `scope` field and recognizes one half-open hexadecimal range syntax. This proves absence of overlap in those recognized scopes, not universal ownership. A separate repository-only search of all task JSON fields found only `P2-csky-recovery-5316` referencing this boundary; its extent `[0x102058A4,0x102058B4)` ends exactly at the new entry and does not overlap. The shared load helper must remain dependency evidence, not newly counted accessor body bytes or newly claimed exclusive ownership.

No new task contract/admission record was supplied. The [workflow contract requirements](../../workflow/CONTRACTS.md) call for schema/campaign/target identity, direct-input hashes, stable image/address-space identity, independent review and serialized owner ledger updates. The standalone results omit several of these normative identity fields. The owner/coordinator should issue the bounded contract, bind this review and exact input hashes, and reconcile coverage by child/image identity before admission. The local packet cannot create its own global assignment receipt.

## Prior payload discrepancy

The unchanged [prior source-map](../../build/pseudocode-first/20260930T190500Z/analysis/csky-recovery-5316/001/source-map.json) states component start `0xC590` plus child `[0x28A0,0x28B0)` but reports payload `[0xF430,0xF440)`. Correct arithmetic is `[0xEE30,0xEE40)`, a `0x600` discrepancy. The new complete-child matching independently confirms the component start. This is a concrete provenance-field defect, not a refutation of the prior decoded semantics or a change in the child image hash.

Before admitting the earlier packet, its owner should add an immutable correction/review record and inspect any downstream payload coverage rows that consumed the erroneous offsets. Preserve the sealed original; do not silently rewrite it. This adjacent defect does not invalidate the new packet's independently checked `[0xEE40,0xEE50)` mapping.

## Limits

Only authorized repository files were read. No denied path was retried, no broad temporary/system inventory was performed, no original C-SKY instruction test or duplicate sealed test ran, and no source/Git/device/campaign mutation occurred. The review checks preserved decoder output rather than independently establishing every ISA encoding; campaign decoder validation remains part of formal admission.
