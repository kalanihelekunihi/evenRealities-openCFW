# Case frame callback: binary framing, DE lines and receive rearm

**4,830 fresh PASS original/independent comparisons** after rebuilding source: 4,800 parser fixtures, 14 resynchronization fixtures and 16 DE-prefix predicates. Per-instruction MMIO hooks assert PRIMASK=1 during receive-start CR1/CR3 updates; restored masks and ordered writes compare. This is bounded callback-prefix evidence, not full timed receive/scheduler integration.

Independent [frame.c](../../components/case/frame_callback_offline/frame.c) reconstructs callback08006544, resync0800a358 and predicate0800be74. Actual ordinary rearm executes HAL080064ec/08008d98 on original and validated independent start source on native. Timed bulk receive080063ec and event post0800a888 **stop before their first instruction**; tests compare call arguments and memory/state at those boundaries without fabricated child return values. Of parser fixtures 3504 return, 120 reach bulk receive, 1176 reach event post (1104 flag0x40,72 flag8). Suffixes after these calls are static reconstruction only.

## Layout and behavior

Scratch current byte20000108, last byte20000109, little-endian u16 count2000010a. Frame storage begins20000974; 1200 bytes end at UART handle20000e24. Event handle is loaded through200000f0. Callback ignores handles whose Instance is not40013800(USART1). One-byte ordinary rearm uses the fixed UART handle and scratch byte; failure posts0x40.

At count0 accepted starters are5A,D,d. Append occurs only for count<1200; updates last byte/count. Case-insensitive DE prefix completes on newline and posts8. Other nonbinary prefixes resynchronize; DE length>=61 also resynchronizes unless newline completion was taken first. Resync retains a trailing5A as a one-byte next prefix only when old count>=2; otherwise resets count0. It does not erase remaining frame bytes.

Binary header is5A A5 type. Type7F uses one-byte length at+3; at count4 requests body into frame+4, length unsigned byte, timeout literal10. TypeCF uses little-endian u16 length at+3/+4; at count5 requests into frame+5, timeout literal20. No units are established by this batch. Only bulk return3(TIMEOUT) is treated as failure by the reconstructed suffix; other statuses advance the u16 count by requested length and load last byte at frame[count-1]. That suffix is not executed by these tests. Further received bytes complete when count equals7F length+5 orCF length+6, and excess count resynchronizes. Type7F/count5 rearms rather than completing; reachability for zero-body frames is not established.

The bulk request has no visible capacity clamp before its call. Requests can exceed remaining1200-byte region in synthetic fixtures; **this proves request arguments, not a hardware overwrite, accepted malformed packet, or safe patch**. Buffer ownership, actual timed UART behavior, frame event consumer and timeout elapsed units remain next dependencies. No public-source attribution or whole-image source/byte equality claim applies to this product-specific callback.

## Reproduce and use

Run build_offline.py --gcc <ArmGNU13.3> --output <scratch>, then opencfw venv Python verify.py <scratch/frame.elf>. See provenance.json, original-disassembly.txt, results.json and reproduction-receipt.json for locked image, addresses, source/tool/output hashes and limitations. Preserve old artifacts; no staging, production writes or device operations performed. Application tooling should distinguish binary length formats and DE newline framing, and treat event8 as completion notification rather than proof of validated payload ownership.
