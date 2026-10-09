# Codec request pack, TX admission and CRC roundtrip

**360 original/source comparisons PASS** bound to the final native ELF. [Reconstructed C](../../components/audio/codec_request_offline/request.c), [interfaces](../../components/audio/codec_request_offline/request.h), [unchanged SDK bridge](../../components/audio/codec_request_offline/hal_bridge.c), [results](results.json), [receipt](reproduction-receipt.json), [image/address hashes](provenance.json). Source tests guard all reached native executable instructions to compiled code; diagnostics, allocation/free and delay/marker fixture boundaries are explicit.

## Recovered request interface

Pack0x57BB0A → send0x57C0D6 → codecUARTTX0x58FB38 → channelTX0x55E7FA → type0 HAL transfer0x58E3F8/0x58E454. Sender uses shared buffer0x2007399C; packer increments shared byte0x20075013 with uint8 wrap. Command encodes `(lowArgument&0xFF)|(highArgument&0xFF00)`, **not the low byte of both arguments**. Header is14 bytes and matches the prior response layout. Any nonzero CRC flag normalizes to wire flag1 and adds4 to declared body length.

The gate is adjusted **wire-body length≤16**, so supported ordinary payload maxima are16 without CRC and12 with CRC. HeaderCRC covers bytes0..9; nonempty, nonNULL body with flag computes trailing CRC over original payload. Pack returns-1 for NULL destination/output-length and-2 for adjusted length>16; rejection preserves destination, output-length and sequence. No capacity parameter or heap allocation exists. Caller must provide backing storage and stable input. Send propagates pack error without TX; successful pack still consumes a sequence even if later TX fails.

NULL payload plus nonzero length is not rejected: body/trailer remain prior destination bytes. Zero payload with CRC declares4 but does not write its trailer. The prior response empty-body CRC bypass therefore permits that header-only/flagged form. These are controlled stale-buffer fixtures, not evidence of device acceptance or data disclosure. CRC corruption and allocation failures are additionally exercised in96 pack→unpack roundtrips using the prior sealed response reconstruction: header failure precedes allocation; body mismatch frees/clears ownership; allocation failure leaves pointerNULL. Response error contracts remain those documented in the prior codec batch.

Malformed input: uint16 adjusted length wraps. Payload65532 plusCRC becomes wire length0 and passes the gate. NULL-body fixtures execute the bounded malformed packing paths. Two nonNULL oversized fixtures **stop before the65532/65535-byte payload-copy call on both sides**; the dangerous copy is not executed or claimed safe. A production API needs checked arithmetic, backing-capacity and NULL/length validation, rather than simply adopting these stock contracts.

## TX lifetime and errors

Channel is narrowed to8 bits;≥4 or descriptor active byte24≠1 returns1. Channel3 descriptor is0x20000D2C+3*28; handle at+4, completion marker+25. Wrapper zeroes a56-byte transfer, sets payload pointer/count and blocking type0, clears marker and calls HAL. Invalid handle/type0 errors and busy-channel errors propagate through channel status1, codec status-1. It **still polls marker up to1000 delay(10) calls after HAL error**, and completion-marker absence does not change a successful HAL return into failure. Selected delay API is explicit synthetic provider; no wall-time assumption is made.

The native type0 bridge validates the original handle magic and calls unchanged selected SDK blocking/nonblocking/FIFO/queue bodies. Other transfer types/DMA remain outside the bridge. Current final native tests do not retain the original channel/type wrapper executable; previous debug compositions did, then were replaced and rerun against the final ELF.

Eight full-FIFO queue fixtures prove synchronous independent admission: all request bytes are copied into the channel3 software queue, FIFO writes remainempty, and shared send buffer is deliberately overwritten with0x33 after return. Queued bytes preserve the prior request. Descriptor completion marker can remain0 through1000 waits while return is0. Thus buffer reuse after this **complete successful blocking admission** does not change those copied queue bytes; it does not establish transmitted bytes, completion, concurrency safety or behavior after partial/error admission. Prior async HAL borrow result remains unchanged and must not be generalized from these successful blocking cases.

## Validation and remaining leads

Exact retained case counts: `codec_channel_tx` 16, `codec_pack` 80, `codec_roundtrip` 96, `codec_send` 168. Total360; two direct pack cases stop before oversized copy. Counts are fixtures, not unique functions or whole-firmware coverage.

Testing uses synthetic always-ready or full UART3 FIFO and synthetic delay/marker delivery; allocation failures/returns are fixtures. No device, actual allocator, callbackIRQ or scheduling was supplied. Header/CRC arithmetic executes source and original instructions. All tests reran after native wrapper/bridge and final header changes.

Next ledger leads remain UART init/close closure, other HAL transfer modes, actual IRQ delivery, shared-buffer serialization and physical codec command semantics. These require separate source/state/trace evidence; this batch neither patches firmware nor claims source exhaustion.
