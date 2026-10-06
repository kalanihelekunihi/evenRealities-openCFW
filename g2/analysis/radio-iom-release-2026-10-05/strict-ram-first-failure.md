# First strict comparison

Input term, prefix03123456, queue03cdcdcd, module0, pending0, hardware index255, end258, PRIMASK0. Final RAM/MMIO/masks matched. Stock update_indices emitted curIdx511 then255 (both PRIMASK1); reused source O2 emitted only255. No source provider was changed.

Final verifier independently asserts these exact per-side index-write sequences and their masked scope; only that contiguous helper-internal sequence is canonicalized to its final write for the call-contract comparison. All other RAM writes, ordered MMIO, full final storage and guards remain strict. Raw per-side writes are saved for every case. No internal RAM-store identity or DMA observer claim.
