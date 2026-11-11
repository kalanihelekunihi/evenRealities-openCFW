# R1 stress authorization and timer controls in C

The normal Clang source build now includes `native_stress_control.c`: authorization enable at `0x4b33e`, mode transition at `0x4b348`, mode setter at `0x4b48c` and periodic callback at `0x4b4a8`. The two existing assembly event adapters execute unchanged and now resolve to these C services.

The direct enable preserves the raw enabled value, forwards authorization slot 1 and returns its result. The event adapter retains its own length gate and boolean conversion. The setter accepts modes below 2, runs transition effects before storing the requested byte, and ignores its length argument. Leaving mode 1 releases a nonzero timer before clearing its cell. Entering mode 1 creates a missing timer with a 3,600,000 period and the periodic callback; creation logging still occurs if the returned handle is zero. Equal modes only log. Logging flags retain their short-circuit reads.

The canonical eight-byte owner at `0x20006eb4` starts with mode 2 and a zero timer. Execution of the stock startup decompressor authenticates all eight bytes; the C object matches them with alignment 4. Its end is the existing activity accumulator start at `0x20006ebc`.

Verification compared 1,458 stock/C direct, actual event-adapter, provider-mutation and mixed-sequence cases. It checked provider order and arguments, guarded state, the public authorization return, preserved registers, stack pointer and interrupt masks. Eight compiled defects were rejected: normalized raw enable, wrong authorization slot, widened mode bound, wrong period, early or missing timer clearing, early mode storage and wrong callback enable value. The normal implementation was rerun afterward.

REA returned the complete 168-byte transition span; it matches the official raw artifact. See [REA receipt](stress-control-c-rea.json), [initialization receipt](stress-control-initialization.json) and [structured review](stress-control-c-review.json).

All 759 R1 units compile and both payloads compose without duplicate strong symbols. All 758 prior object hashes are unchanged. Application imports decrease from 131 to 129; bootloader imports remain 34. The R1 source check passes. Global `make sources-check` still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

Authorization, timer allocation/release and logs are modeled boundaries. Callback identity and direct execution are checked; asynchronous scheduling and physical sensing are unproved. Private scratch and caller-clobbered registers are excluded. This is relocatable source composition, not a complete linked or device-tested firmware image. Byte identity is not required for this implementation route.
