# Shared flash state reconstruction

`runtime_gx8002_flash_state.h` defines the same 32-byte state for discovery,
initialization, word I/O, information queries, OTP region accessors, and the
state definition itself. It replaces incompatible prefix-struct and word-array
extern declarations. The admitted function payloads remain unchanged after
this migration; all affected decoded comparisons pass.

The fields are device index, usable size, address-byte count, selected-device
address, an eight-byte command scratch buffer, and typed word-program/read
callbacks. Static assertions preserve the total size and command/callback
offsets. The initial source object sets index to -1 and all other fields to
zero, producing exactly the original 32 bytes at package 0x184f8.

`verify_gx8002_flash_state.py` recompiles the state, compares its target layout
and bytes, rejects relocations, and compiles all six source modules together
to check declaration compatibility. Every affected function builder records
the shared header hash as part of its reviewed provenance.

Source ownership of this state does not establish full startup operation.
The device/interface tables, remaining callbacks, and the initializer's
larger frame/end-to-end behavior still require recovery or qualification.
