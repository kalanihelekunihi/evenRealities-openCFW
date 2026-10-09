# GX8002 response framing, CRC and owned message

**360 original/source comparisons PASS**, bound to the final native ELF. [Readable C](../../components/audio/codec_response_offline/response.c), [layout/interface](../../components/audio/codec_response_offline/response.h), [results](results.json), [receipt](reproduction-receipt.json), [image/function/data provenance](provenance.json).

The actual chain is send/wait0x57C512 → read wrapper0x57C442 → blocking reader0x57C1FC → codecUART read0x58FB2A. On read success the send/wait caller performs UART cleanup0x57BAEC **before** unpack0x57BD06. Neither read function validates magic/CRC. The unpacker performs those checks. Other static callers include MicDelay1Bit0x57D1CC and GetVoiceEvent0x57DA40; their device interactions/retries are not executed here.

## Wire and ownership

Header14 bytes: `BUXX` at0, command little-endian uint16 at4, sequence byte6, flags byte7, body-on-wire uint16 length8, headerCRC32 little-endian at10 over wire bytes0..9. Bit0 of flags means the declared wire-body length includes a trailing4-byte bodyCRC. Payload excluding CRC is limited16. Original0x58FAAC calls CRC0x4D34C4 with NULL prior state. All256 locked table entries at0x699BA8 match reflected0xEDB88320; initial/final complement and prior-finalized-CRC chaining match16 independent zlib vectors, including empty,123456789,all256bytes and supplied prior states. Standard 123456789 CRC isCBF43926.

Unpacker copies14 header bytes into output before magic/size/CRC validation. It computes total in uint16 (declared+14), checks available, then verifies headerCRC before allocating. For nonempty payload it allocates exactly payload length, copies bytes into owned storage, records pointer at14 and length at18; optional trailer is copied to20. BodyCRC failure frees allocation and zeroes pointer, but retains payload-length field. Success records total at24. Free helper clears pointer and length only when pointer was nonzero. Callers must not treat retained metadata on errors as an owned valid message.

Return map: -1 invalid inputs/short header; -2 magic; -3 insufficient declared frame; -4 headerCRC; -5 payload>16 (including CRC-flag underflow); -6 allocation failure; -7 bodyCRC. Header-only success sets pointer/length0. **CRC-flagged empty payload (wire length4) bypasses trailer CRC verification entirely**, including corrupted synthetic trailer. This is a recovered quirk, not a recommended parser rule. Trailing bytes beyond computed total are ignored by unpack; selected send/wait does not compare command/sequence to an expected request.

## Blocking reader and deadline

Reader consumes14 bytes before validating advertised capacity against uint16(declared+14). Tests deliberately allocate ample real backing storage while advertising capacity1; they prove14 bytes are written on this path without inducing a host overflow. A future safer implementation needs an early header-capacity check. Declared65535 wraps total to13 and can return14 after header read when capacity≥13; unpack subsequently rejects excessive payload. No CRC/magic or resynchronization is performed by reader.

Both header and body share the initial deadline. Tick wrapper0x58FAC8 zero-extends32-bit kernel ticks; reader subtracts them as unsigned64-bit elapsed and compares against uint32 timeout before drain. At tick wrap the elapsed underflows to a huge64-bit number and expires on the observed next check. This differs from the prior one-byte absolute-deadline helper. Timeout0 rejects even staged bytes. Units are OS ticks; no milliseconds claim. Arrival/replay/delay are synthetic and finite, not measured physical serial timing.

## Executed scope

68 unpack fixtures cover valid/invalid magic/header/bodyCRC, length0/1/2/16/17, short frames, allocation failure, CRC-flag underflow and uint16 wrap;16 CRC vectors;4 free fixtures;224 actual response/drain fixtures;12 wrapper fixtures;36 unchanged send/wait compositions with stock versus reconstructed read/unpack children. Both sides run original tick wrapper; native side uses prior sealed ring drain. Original CRC/magic/memory-copy instructions execute unmodified. Diagnostic flags are forced disabled; diagnostic sink is no-op. Allocation/free and kernel tick/delay/arrival are explicit synthetic providers. Compositions additionally stub init/send/cleanup and do not prove UART open/close, request transmission, heap fragmentation or real codec response. Native child redirection is fixture instrumentation, not a firmware patch.

Follow-on scheduler composition is [resume/yield](../audio-resume-yield-composition-2026-10-09/REPORT.md). Pending-ready scheduling still needs actual exception delivery/whole initialized task state for live ordering claims. Codec command semantics, request pack/TX closure, physical response acceptance and allocator concurrency remain bounded follow-on leads; this batch does not declare source exhaustion or firmware completeness.
