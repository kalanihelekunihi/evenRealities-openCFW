# LIS power and register-17 C integration

The public entries `r1_lis_native_power_mode_set` at `0x7575a` and
`r1_lis_reg17_bit6_enable` at `0x7518a` now use the existing C bodies in
`native_lis_setup.c`. Four duplicate public bridges were removed from that
file, and its unique C bodies now participate in normal relocatable
composition. Its transport declarations use the canonical ST header.
The two C bodies retain their previous compiler instruction bytes.

REA analysis and native execution support both changes. Each public entry
retains a 10-byte frame bridge. The stock routines are 106 and 44 bytes;
the current C bodies are 112 and 44 bytes, respectively, in addition to the
bridges. This conversion does not establish byte identity.

Power setup uses the native mapping of input bits into registers 0x20 and
0x25, which differs from the modern ST power enum. It stops on errors in the
first read or first write. A failed second read still leads to its field
update and final write; those last two statuses are added with unsigned
32-bit wraparound. Register-17 setup sets bit 6 after a successful read and
returns the subsequent write status, or returns the read failure unchanged.

The power frame retains incoming R2/R3 words at entry SP-24 and SP-20;
register-17 retains incoming R3 at SP-16. Their scratch bytes are not
initialized, so successful non-writing reads use the captured seed. Callback
changes survive final scratch-word restoration.

The ignored `build/goal-r1-lis-power/verify.py` probe passes 10,240
stock-versus-C scenarios: 5,120 per entry. Actual C bodies and transport
wrappers execute. An independent mask and status oracle checks each update.
Coverage includes all low-byte input values, every scratch seed byte, all
read-fill masks, full-width inputs and statuses, failures at each I/O step,
overflow in the final power status sum, retained-pointer changes, and live
transport callback/handle replacement. Checks include call arguments/order,
context and scratch accesses, full return words, restored R2/R3 as applicable,
callee-saved registers, SP, interrupt masks and callback alignment.

The other 22 function bodies in `native_lis_call_frames.c` are unchanged.
The full R1 build compiles 562 units without failures or duplicate strong
symbols. Application composition now includes 451 objects; imports remain
227 application and 34 bootloader. Exact source, manifest, stock, REA and
probe bindings are in [the machine-readable review](lis-c-power-review.json).

Final bus callbacks are modeled. The C bodies add callback stack depth below
the preserved scratch words. Physical sensor behavior, timing, complete
fault-state equivalence, final linking, provider qualification and byte
identity remain unproven. No G2 gates or source-plan selections change.
