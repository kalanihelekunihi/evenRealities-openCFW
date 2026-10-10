# Nonblocking SPI full-duplex source provenance and contract

## Useful new public source

Official Ambiq public commit `ef488e3b1fb1d612d61862595edd203ee9f6ca37` contains `am_hal_iom_spi_nonblocking_fullduplex`, absent from registered commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`. The latest file-changing public commit query, checked 2026-10-09, reports May 12, 2026. This is an availability pin, not the first introduction date, named SDK release, or proven stock producing revision. Two public files were acquired under `public-source-ef488e3/`, retaining their explicit BSD-3-Clause notices; hashes/URLs are in `PUBLIC-ACQUISITION.json`. No code was executed and no submodule/index changed.

Public source: https://github.com/AmbiqMicro/ambiqhal_ambiq/blob/ef488e3b1fb1d612d61862595edd203ee9f6ca37/mcu/apollo510/hal/mcu/am_hal_iom.c

This public implementation supports TX DMA with RX FIFO/IRQ. SDK 5.2 additionally supports selectable RX DMA with TX FIFO/IRQ. Do not treat the public pin and SDK as interchangeable.

## Exact provenance comparisons

Registered working-tree IOM C/H both equal their pinned Git blobs. Old pin has no FDNB API, helper/state or mode enum. Complete source SHA-256 pairs and authenticated ZIP members are retained in `PROVENANCE.json`; full old-to-SDK and public-to-SDK textual differences are retained separately.

Six complete function text comparisons, including their parameters and entire bodies, are in `PUBLIC-SDK-FUNCTION-CHECK.json`. Public and SDK RX FIFO drain helper are exactly identical (605 bytes, SHA-256 `28b962c9d7b4514290f909437de4d30d869dae1ade4e4b65a82e540fef99552b`); `am_hal_iom_status_get` is also identical (1230 bytes). Public lacks the TX FIFO fill helper. Finish, interrupt service and FDNB start functions differ. These are exact source-text comparisons, not compiled stock matches.

Authenticated release history identifies SDK 5.2.0, July 24, 2026, `release_sdk5p2p0_66487dd10`; it explicitly adds selectable DMA direction for hybrid nonblocking SPI full duplex relative to 5.1.0 (line 142). Receipt: `RELEASE-HISTORY-PROVENANCE.json`. The registered older source lacking even the one-direction API illustrates why nominal 5.1 labels cannot uniquely select a source body.

## SDK 5.2 API and completion contract

- `eFdnbMode=0` selects RX DMA/TX IRQ. The named TX DMA/RX IRQ enumerator selects the opposite direction; every other enum value also falls back to RX DMA/TX IRQ in the start function. The new enum field is inserted before `ui32PauseCondition` in the transfer structure. This is an ABI discriminator; do not assume an old caller's structure has the new interpretation.
- Header documents a callback `(context, transactionStatus)` on completion. Its API summary still describes TX DMA/RX FIFO only; implementation and enum also support the RX DMA direction. Source governs this discrepancy.
- Validation-enabled builds reject invalid handle, null transaction, non-full-duplex direction and zero length, then call `validate_transaction(..., true)`. SPI mode and no running sequence are required even without optional API validation.
- Within the interrupt-disabled start section, active FDNB, high-priority activity or pending transactions returns INVALID_OPERATION; non-idle or active hardware command returns IN_USE. Rejection returns synchronously without invoking this transfer's callback. SUCCESS from start means scheduled, not complete.
- Start saves INTEN/DMATRIGEN, clears accumulated interrupt status, sets one pending transaction, enables full duplex and retains caller TX/RX pointers and callback/context. One direction is DMA; the other uses byte-oriented FIFO helpers. Caller buffers remain live until completion. It installs THR plus CMDCMP/DCMP/error interrupt enables, then issues CMD and restores the master interrupt state.
- Interrupt service accumulates interrupt bits. TX-DMA mode drains RX on entry; RX-DMA mode fills TX on threshold interrupts. Errors are decoded/reset before finishing with the resulting error status.
- With CMDCMP accumulated, TX-DMA mode drains RX again and succeeds only when RX bytes left is zero; idle hardware with bytes left finishes FAIL. It does not separately require accumulated DCMP in this branch. RX-DMA mode waits for DCMP when DMA bytes is nonzero, then requires no remaining TX bytes and idle/no active command; idle with TX bytes left finishes FAIL. Earlier service calls can return SUCCESS while still active. A FAIL passed to the callback by these idle/residue branches does not itself change the service function's final SUCCESS return.
- Finish snapshots callback/context, clears active state, counters, buffer and callback pointers, pending count and accumulated interrupts; disables DMA, restores DMATRIGEN/INTEN and clears FULLDUP; then calls the saved callback if non-null. Thus callback observes cleared transfer state and restored enables. Actual IRQ delivery/reentrancy remains a platform matter.
- `status_get` returns current hardware idle/error/command flags and DMASTAT plus software pending count under a critical section. Its SUCCESS return reports a successful status query, not transaction completion or the callback's result.

## Finite stock/version discriminators for the implementation owner

1. Presence of the FDNB start API and RX FIFO-drain/finish state excludes the registered pre-FDNB source for that target.
2. Presence of `eFdnbMode`, TX FIFO-fill helper, RX-DMA programming branch and DCMP gate discriminates supplied selectable-direction SDK source from the public TX-DMA-only pin.
3. Retained-pointer/counter state, saved interrupt/trigger restores, and callback-after-clear sequence provide a multi-feature contract for a stock-bound comparison; a common FIFO loop alone cannot establish inclusion.
4. Field interpretation in the actual caller, state offsets, complete function extents and error/completion branches must agree before admitting either provider. Source family/API presence and exact public-to-SDK RX drain equality do not prove linked stock identity.

Proposed reference for owner review: add a separately pinned newer Ambiq reference at `ef488e3b1fb1d612d61862595edd203ee9f6ca37` only if the owned stock target benefits; preserve existing 5efc reference rather than re-pin it. The isolated acquired C/H files already permit this bounded review without a new checkout. Stop discovery here until stock mapping distinguishes the one-direction and selectable-direction variants. No proprietary archive redistribution, production edit, device operation, or closed STRDIS/CMSIS probe occurred.
