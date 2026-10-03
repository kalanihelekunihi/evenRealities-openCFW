# Independent review 6529

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet artifacts, source hash, and copied 544-byte interval match. The 41B8F8 map confirms the relevant routine rejects a null destination and unsigned indices `>= 34`, then computes the source from the literal at 41C310 plus `16*index` and calls 4156AC with length 16. I independently checked the LDR.W at 41B906: its aligned-PC-relative target is 41C310, whose pinned word is 0x430660. The selected addresses therefore span 0x430660 through 0x43087F, with exclusive end 0x430880. All 34 extracted records are exactly 16 bytes and concatenate byte-for-byte to the source slice.

This supports the conditional table extent implied by the mapped consumer. The field purpose and copy-child behavior remain unclaimed; numeric values do not establish MMIO semantics. Decoding 41C310 as Thumb code would conflict with the verified literal consumer, but the word’s numeric value alone is not used to infer purpose. No canonical files or gates changed.
