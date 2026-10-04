# P2-9055 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 184 instructions match the pinned image byte-for-byte.
- Producer and consumer compute bytecount as low8(count*32), gate around the operation, and compare available/used bytes before modifying state. Producer’s null-buffer path still advances write index and used count; consumer’s null-buffer path similarly advances read index and reduces used count.
- Each copied byte is handled with fresh state/index/storage reads. Index updates wrap to 32 bits then reduce modulo capacity using UDIV/MLS. Both paths restore PRIMASK from the saved gate result, return low-byte success, and leave the saved prior mask in R1.

Limitations:

- Malformed state, capacity zero, storage validity, aliasing and concurrent producer/consumer effects are not resolved; arithmetic wrap behavior is preserved from the code. Gate semantics and physical transport are not claimed.
