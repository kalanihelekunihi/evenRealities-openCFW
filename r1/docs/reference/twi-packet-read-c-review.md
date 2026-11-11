# R1 hardware TWI packet reads in C

Current implementation: [ordinary C read status ABI](twi-read-pure-c-review.md). Read-wrapper scratch-register/frame preservation described below is historical.

Both packet-read operations in `native_hw_twi_operations.c` now use direct C
control flow. The assembly push/call/pop bridges and their out-of-line helper
kernels are removed. Empty register/SP observations remain to preserve the native
saved-R3 overlay. This is a compiler-profile-specific candidate, not portable
ISO C or an exact-byte admission.

REA corroborates the locked stock operations at `0x55414` and `0x55448`. Both
return 9 for a null request, 8 for a closed bus, and 12 for any nonzero read-adapter
result. The primary path loads 16-bit register and length fields; the secondary
path loads only their low bytes. The output pointer is a word at request+12.
The outgoing fifth argument is the instance at cluster+28. Stock stores it over
saved R3 before loading the packet fields, so R3 on return contains the instance
or a subsequent provider mutation. Early exits restore incoming R3. The C path
retains these behaviors, including the explicit store before packet loads.

Normal Clang uses a 16-byte provider frame; stock uses eight bytes. This frame
change is recorded, not treated as identical. At the read-adapter boundary, all
R4-R11 values match stock and final SP, masks, R0 and R3 match in the tested cases.
10,752 direct pairs cover both buses, opened values 0/1/255, null requests,
length/register boundaries, raw statuses, provider writes to the outgoing word,
and request alignments 0 through 3. A further 16,128 pairs execute the actual C
register-read adapters with modeled legacy TX, SDK RX, and wait providers. Their
private register-buffer pointers are normalized; output bytes and bus state match.
Five negative controls reject wrong null status, widened secondary fields,
truncated error status, and lost saved R3.

The normal product object has the same read bytes and relocations as the probe.
Both write functions retain their prior bytes and relocations; all other 588 R1
objects are identical. All 589 units compile and compose, unresolved imports
remain 164 application / 34 bootloader, and no duplicate strong symbols appear.
Qualification selects no new regions. The canonical hybrid application retains
its locked SHA with 4,245 source-built, 641,915 binary fallback and 248 resource
bytes. The source plan is unchanged; complete source-only rebuilding is unproven.

Only the normal Clang profile is validated. Arbitrary private-stack aliases,
faults, concurrency, electrical behavior, DMA and real interrupt delivery remain
unproven. See `twi-packet-read-c-review.json` for hashes, exact report pointers,
REA evidence, checks and negative-control results. Reproducible probes live under
ignored `build/goal-r1-twi-packet-read-c/`.
