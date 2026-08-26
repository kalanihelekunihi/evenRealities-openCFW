# Cordio `attc_write.c` source recovery

## Result

The stock interval `[0x00539DCC,0x00539E48)` is the complete linked Cordio
optional ATT client write unit. It contains two contiguous functions / 124
bytes. Of five source definitions, `attcPrepWriteAllocMsg`,
`AttcPrepareWriteReq`, and `AttcExecuteWriteReq` have no bodies, callers, or
stored pointers and are dead-stripped. The preceding bytes are another
translation unit's literal pool, and `0x00539E48` begins unrelated HCI code.

The selected Apache-2.0 source is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, Git blob
`7602baa5ffa944a96757a9f36f5ee517aa4754fd`, 6,997 bytes, SHA-256
`def6d08036fdaed16a97483858ef8f37c3a49f114122aad0dcffd4ba41c8688e`.
It is byte-identical through r20.05–r20.05c and to the later official
AmbiqSuite R4.4.1 import.

This unit is deliberately not treated as an independent release
discriminator. Both linked definition bodies are byte-identical in the
r19/AmbiqSuite 2.x and r20 source families. The r20 selection follows the
already-proven client response table, EATT control-block ABI, and per-bearer
request machinery rather than evidence unique to these 124 bytes.

## Boundary, ingress, and behavior

The physical interval and concatenated bodies both hash to
`72a705a886cf5ec553b89b61f9480e21cc672b35676cbac9fbd9cf2f2ac4adc9`.
This source has no retained path or owned literal tail.

`attcProcPrepWriteRsp` is stored in response-table slot 11 at `0x00700990`.
It terminates continuation after the final prepared chunk and removes the
handle/offset fields from the callback value view. `AttcWriteCmd` has one
product caller; it allocates and encodes opcode `0x52`, handle, and value, then
passes ownership to `attcSendMsg`. Exhaustive scans find one direct call, one
stored entry, and no branch or pointer into a strict function interior.

## Reproducibility

`tools/analyze_g2_cordio_attc_write.py` pins the image, both bodies, complete
physical interval, response-table cell, sole direct call, sole stored entry,
and zero strict-interior ingress. The full ledger is
`tools/manifests/packetcraft-cordio-attc-write-function-map.tsv`; provenance
is recorded in `tools/manifests/packetcraft-cordio-attc-write-provenance.tsv`.

## Production replacement

`components/shared/cordio/runtime_cordio_attc_write.c` now maintains all five
source definitions. Two guarded redirects replace the complete 124-byte linked
stock interval with 144 compiled Cortex-M55 bytes plus two alignment bytes
under two strict relocations. The three dead-stripped allocation,
prepare-request, and execute-request helpers are independently target-compiled
without inventing stock coverage.

Host execution covers continuation termination, response value adjustment,
write-command encoding and ownership transfer, copied and referenced prepare
writes, execute/cancel flag encoding, allocation alignment, and allocation
failure. The canonical overlay is 347,282 bytes, SHA-256
`3387c6fcb18b78ad7d8244f0b0392baa51d86a9eca47686ca9205a0d852d191f`;
the Apollo component is 3,870,678 bytes, SHA-256
`30bc664a940698698245dd117bfb127d9202e216c51a00826f0f030b31d5c468`;
and the deterministic package is 4,649,172 bytes, SHA-256
`777a059d84671ee04460d7c9cdb9af9ab93ce7eaaced0932b0c254f9f2a53e77`.
Live ATT peer, controller, continuation, and buffer-lifetime validation remains
blocked by unavailable authorized responsive G2/EM9305 physical evidence. No
image was signed, flashed, or installed.
