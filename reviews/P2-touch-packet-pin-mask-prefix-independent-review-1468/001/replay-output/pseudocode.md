# Packet pin-mask prefix at 56A4

The prefix [56A4,56F4) is 80 instruction bytes. Save a nine-word frame and allocate 36 scratch bytes. Start a zero mask. Traverse descriptor word +20 records with stride 8, count from configuration halfword +12; OR 1 shifted by record byte +5. Then traverse descriptor word +24 records with the same stride, count from configuration byte +44, and OR the corresponding shifts. Register shifts at least 32 contribute zero. Retain descriptor/context pointers for the remaining body.

Forty-five original-instruction fixtures check zero/nonzero counts, two-list union, shift boundaries, stop PC and 72-byte frame. This is only a bounded prefix; the packet-building suffix and full return are unresolved. No canonical admission or C implementation.
