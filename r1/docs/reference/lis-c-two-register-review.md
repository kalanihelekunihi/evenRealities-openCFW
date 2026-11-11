# LIS two-register setters C integration

`lis2dw12_data_rate_set` at `0x75120` and `lis2dw12_filter_path_set` at
`0x75450` now use the existing ST-attributed C bodies in
`board/sensor-kernels/lis-setup/st-setup-frames.c`. Those C sources are
unchanged. The public entries in `native_lis_call_frames.c` retain only
10-byte frame bridges. REA analysis and stock execution support both changes.
Each native entry is 92 bytes; the current C bodies are 92 and 98 bytes,
respectively, in addition to the bridges. This does not establish byte identity.

The bridges retain incoming R2/R3 at entry SP-24 and SP-20. The two native
scratch bytes therefore keep their input seeds when reads do not fill them.
Data-rate setup updates ODR bits in register 0x20, then sleep-mode bits in
0x22. Filter-path setup updates FDS in 0x25, then user-offset routing in
0x3f. Both sequences stop on any nonzero read or write status and return that
full word. The final pop restores both scratch words, including callback
changes to their other bytes. No zero initialization or extra error policy
is introduced.

The ignored `build/goal-r1-lis-two-register/verify.py` probe passes 10,240
stock-versus-C scenarios: 5,120 per setter. Actual C bodies and transport
wrappers execute. An independent byte-mask oracle checks each update.
Coverage includes all 256 low-byte input values, every scratch seed byte,
all read-fill masks, full-width inputs and statuses, failures at each I/O
position, changes through retained scratch pointers, and live transport
callback/handle replacement. Checks include call arguments/order, context
and scratch accesses, full return words, restored R2/R3, callee-saved
registers, SP, interrupt masks and eight-byte callback alignment.

The other 22 function bodies in the public-entry compilation unit are
unchanged. The full R1 build compiles 562 units without failures or duplicate
strong symbols; imports remain 227 application and 34 bootloader. Exact
source, manifest, stock spans, REA analyses, integrated sources and probe
bindings are in [the machine-readable review](lis-c-two-register-review.json).

Final bus callbacks are modeled. The C bodies add callback stack depth while
preserving native scratch addresses. These are partial C extractions;
physical ODR/filter behavior, timing, complete fault-state equivalence,
final linking, provider qualification and byte identity remain unproven.
No G2 workflow gates or provider selections change.
