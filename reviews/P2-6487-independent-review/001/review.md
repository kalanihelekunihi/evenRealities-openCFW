# Independent review 6487

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet files and F43029C..F430372 source span match the locked image. GNU Thumb decoding confirms the ordered type-4 check and its ignored 41D92C call, followed by the type-2 check and its separate field reads. On the type-2 path, byte 6 is freshly read and masked to two bits before BFI into R1 bits 6–7; a fresh record-word-0 load is passed to 41D92C. The code then freshly rereads byte 6 and record word 8 for early exits.

If those checks pass, word 0 is saved at SP+0 and 415FF4 receives (SP+4, 28). The subsequent dynamic bitset index comes from a fresh SP+0 load, masks its low five bits for the shift, shifts the full word by five for the indexed store, and writes through SP+4 without an in-span bounds guard. Calls then occur in order to 41DCCA(0,1,SP+4), 41DE3C(0,SP+4), 41E000(0,fresh word at record+8,fresh SP+0,0), and 41DA84(0,1,SP); their return values are not tested here. Finally, a signed-halfword table lookup based on a fresh word-0 load shifted right five calls 43025C(value,4), then a second fresh word-0 load and lookup calls 430240. The shared loop continuation resets the stride on its next iteration.

These are instruction-level facts for this span. The stack-index store is not proven bounded, the calls' external semantics are not established, and no full record/table interpretation is implied.

No canonical files or gates changed.
