# R1 buttonless DFU event policy in C

`board/native_dfu_event_policy.c` implements the registered callback at stock `0x5232c` and its disconnect helper at `0x5c58c`. Both bodies use typed SDK interfaces and add no assembly or mutable state.

Prepare initializes a fresh 44-byte advertising configuration through the existing initializer and cached-record getter, sets `ble_adv_on_disconnect_disabled=true`, then copies it into existing advertising instance B at native `0x200082b0`. The actual SDK connected iterator then calls the actual C disconnect helper with null context for each captured connected handle. Each callback requests S140 disconnect reason `0x13`; nonzero results only add warning diagnostics. The final reported count is callback attempts, including unsuccessful disconnect requests.

Enter, enter failure, response-send failure and unknown events retain their distinct diagnostics. They do not issue advertising changes, disconnects or a boot request. The SDK owns subsequent bootloader entry; this policy does not independently initiate it.

**5,708 stock/C comparisons pass**. The real advertising initializer/getter, cached class owner, both advertising instances, SDK configuration copy, connected iterator, atomic flag getter, C memory routines and checked DFU initializer execute in the fixture. Cases include all 256 event-byte values, all 20 connected bits, ignored high bits, independent configuration reads, SDK result patterns, live backend mutations, captured iteration state and initializer/callback delivery. All **13 compiled defects** are rejected.

The replay executes all **446 reachable native instruction bytes** in the two routines. The remaining two bytes at `0x5243e` are an unconditional branch with no predecessor in a direct-control-flow overapproximation from the legal entries. They are documented as unreachable, rather than counted as dynamically covered. The CFG assumes no arbitrary external jump into a function interior, corrupted return or synthetic exception resume.

Logging, full 124-byte cached reads, S140 disconnect results, DFU initialization acceptance and the error handler are modeled. The SDK configuration and iteration entry hooks observe their real bodies without replacing them. The iterator's captured flags remain authoritative even if a disconnect backend changes the global connection flags. Callee-saved integer/FP registers, masks, SP, stack/state guards, complete advertising storage and public traces are checked; source execution cannot enter stock code. No physical peer is disconnected and no firmware upload, flash write, reset or bootloader entry occurs.

The normal build compiles **851 units**: 769 application and 82 bootloader. The buttonless policy import closes without new imports, leaving **67 application imports** and 22 bootloader linker imports. All **840 prior nongenerated objects** remain identical. R1 manifest checking passes. Repository-wide checking retains the unrelated unlisted G2 `resident_rom_thumb_set.S` issue. Final source placement, linking, device boot and physical DFU behavior remain unverified. Byte identity and paid compilers are not requirements.

Exact hashes, REA reads, control-flow evidence, test groups and limits are in [dfu-policy-c-review.json](dfu-policy-c-review.json). No commit or device write was performed.
