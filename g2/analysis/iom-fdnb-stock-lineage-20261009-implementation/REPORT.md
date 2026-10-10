# SPI full-duplex lineage: bounded stock binding

**OLD dispatch behavior in the selected stock interrupt-service provider.** Its direct high-priority dispatch lacks the new SDK 5.2 FDNB-active branch. The selected stock full-duplex provider is blocking; its upstream blocking source body is text-identical between the prior registered source and SDK 5.2, so that provider alone cannot distinguish revisions. No global absence of asynchronous SPI is established.

Authenticated locked Apollo main payload SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`. Mapping: virtual address minus `0x438000` plus 32 gives original payload offset. Original bytes, range hashes and source hashes are in `stock-receipts.json`; independently replayable instruction assertions are in `verify.py`.

| Stock provider | Code extent | Bytes | SHA-256 |
|---|---|---|---|
| Blocking SPI full-duplex | `0x55CF40..0x55D246` exclusive | 774 | `3fb2e8b8e56cad942a066eb0e3eb2bd64b59db27e11ecb6d6acd7e0c8f776424` |
| Interrupt service | `0x55C558..0x55C7E0` exclusive | 648 | `21b13723f979dd5eb36302ffe18d9ee5fd1728d6834cf64f59e5d5067a94a8b8` |

Stock blocking identification rests on direction==2 validation at `0x55CF6E..0x55CF74`, transaction pointer in r9, `validate_transaction` call `0x55CF80` with r2=1, pending-transaction and hardware-status delay checks at `0x55CFE4`/`0x55D008`, saved INTEN and interrupt-disable stores at `0x55D016..0x55D022`, DMA disable at `0x55D02E..0x55D034`, FULLDUP set at `0x55D0C8` and MSPICFG store `0x55D0D0`, CMD store `0x55D0D8`, FIFO polling loops, then INTEN restore and FULLDUP clear before the terminal POP. IOM base is `0x40050000`, module from handle+4, stride `0x1000`; MSPICFG offset `0x280`, CMD offset `0x120`. The literal dependencies are separately receipted. Prologue-through-return envelopes do not claim byte equality to a rebuilt source object.

The service discriminator is immediately after handle validation: `0x55C57A` loads module from handle+4; `0x55C57C` loads the byte at handle+`0x83C`; `0x55C580` tests zero; `0x55C582` branches to `0x55C67E` when zero, otherwise it accumulates the interrupt mask at handle+24 and enters high-priority completion processing. The callback/HP ring path and the zero-branch pending/CQ processing agree with the old source's `if (pIOMState->bHP)` then ordinary queued handling. No FDNB-active test, mode dispatch or RX-drain/TX-fill call precedes it. The seven exact instruction assertions in `verify.py` anchor this finding to original bytes.

SDK source delta, read in memory from the user ZIP:

- New `am_hal_iom_spi_nonblocking_fullduplex(handle, transaction, callback, context)` at C lines 4574–4705, versus old two-argument blocking API. The four pointer arguments conventionally occupy r0–r3 on Arm; no compiled new entry was located or ABI-certified here.
- New transaction field `eFdnbMode` at header line 397, inserted after priority and before pause/status fields. Default 0 selects RX DMA/TX IRQ; 1 selects TX DMA/RX IRQ. The field may occupy old padding under short enums or shift later fields under 32-bit enums. Under ordinary 4-byte enums/pointers and 8-byte uint64 alignment, old pause/status offsets 36/40 become 40/44, while total size stays 48 due to old tail padding. Exact stock/new offsets require compiler enum/alignment options or a producing object; no conditional layout is admitted as actual ABI.
- New private `sFdNb` state includes activity/mode, buffers/counts, saved interrupt/DMA trigger configuration, callback and context. New nonblocking entry validates, enters an interrupt critical section, rejects active/HP/pending use, saves state, chooses one DMA direction, optionally primes TX FIFO, enables FDNB interrupts, submits CMD and returns. Completion belongs to service/helpers rather than an entry-local polling loop.
- New service at C lines 3195 onward dispatches `sFdNb.bActive` before bHP, accumulating interrupts and choosing `iom_fdnb_drain_rx_fifo` or `iom_fdnb_fill_tx_fifo`, with error/completion work through `iom_fdnb_finish`. This branch is absent from the selected stock service's authenticated dispatch.

Conclusion: the unchanged SDK 5.2 FDNB service path is not the selected stock provider's control flow. The blocking provider remains compatible with both versions' identical blocking source body. A private patch, unused/new API removed by linking, a separate service, or a mixed tree remains possible; neither whole-SDK provenance nor whole-image FDNB absence follows. Physical bus behavior, DMA/IRQ timing, device capability and live reachability were not tested. No compiler/firmware/device execution or generic byte scan was performed.

Next input needed for a stronger claim: an independently anchored stock nonblocking full-duplex entry/caller or complete IOM reachability boundary, plus exact new producer enum/alignment configuration or object for ABI equality. These inputs do not block this finite old-service-dispatch conclusion. Unresolved call dependencies in the blocking provider remain labeled and were not executed/reconstructed.

Preservation: 3445 prior sealed entries match under existing policy exclusions; 110 audit inputs and four checkpoints match; index unchanged. Only this analysis directory was written. No production, submodule-pin, device, commit, push or index changes. No closed audio/DSP/LZ4/Nema tests were revisited. Prior STRDIS outputs remain sealed and unchanged.

Replay: `python3 g2/analysis/iom-fdnb-stock-lineage-20261009-implementation/verify.py`. This task applies no relevant local skill.

The independent proposal `../dependency-gap-audit-fresh-2026-10-09T192823Z/next-sdk-audit/SPI-FDNB-BOUNDED-CONTRACT.md` agrees: all offsets are conditional, and its 12 synthetic fixture positions require an authenticated new stock entry/state/dependency gate. This pass stops at old-service dispatch; none of those fixtures was executed.
