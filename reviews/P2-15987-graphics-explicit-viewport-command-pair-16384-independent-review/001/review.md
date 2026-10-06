# Independent review 15987

Partial, accepted:false. Fresh decode replay passed for 50 bytes. Computes wrapped end X/Y before clipping negative start X/Y to zero, packs low16 start coordinates, calls command 272, then packs the precomputed end coordinates low16 and tail-branches command 276 after restoring local frame. First child result is discarded.

Child/global/hardware effects remain unqualified; no admission or gate change.
