# Native Goodix record destructors in C

The [machine-readable receipt](goodix-native-record-teardown-c-review.json) pins the ordinary C implementation in `r1/src/application/goodix/native_record_teardown.c`, stock bytes, normal build and executed fixtures. Behavioral agreement is the admission criterion; byte identity is not claimed.

The common destructor at `0x29354` accepts null; otherwise it releases nonzero pointers at offsets `1c0,1dc,1f4`, then releases the root allocation. Fields are not cleared. Wrappers `0x5a628` and `0x34a38` tail-enter this same function. The extended destructor at `0x3e6b0` first reads and optionally releases its pointer at `260`, then calls the common destructor; it has no initial null guard. The nullable allocation release helpers at `0x36230` and `0x3757c` share one C implementation. All return zero when they return.

Direct comparison passes 576 field-mask/result cases, 80 live-field mutation cases and six null arguments. All 100 native instruction bytes execute. Free is modeled with call-time record snapshots, result variation and caller scratch clobbers. A separate 256-case integration executes the actual C initializer, allocator, free and record destructors with roots before/after child allocations and optional unrelated live allocations. Full heap images and write widths/order/values match. Source execution cannot enter stock code. Nine compiled defects are rejected.

The initial extended-record null access at `260` is checked as an unmapped emulator read, not a physical MCU fault. Other null arguments return zero without release. Saved integer/FP registers, SP, masks, FPSCR and caller guards are checked; caller scratch, APSR and private frames are excluded. Typed records are fixture preparation, not recovered algorithm initialization.

The normal serial build compiles 871 units (789 application, 82 bootloader), with no duplicate strong symbols and unchanged 62/22 imports. The tested object matches its normal object, and all 860 prior nongenerated objects remain identical. Two existing generated objects differ with build directory paths. No writable state is added; source plan and existing cache linker layout remain unchanged.

The typed dispatcher, processing parent, algorithm initialization/computation, concurrency, physical hardware, final executable linking/startup and boot remain open. Relocatable composition is not bootable firmware.
