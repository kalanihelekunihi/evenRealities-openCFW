# Associated initializer R2 crosswalk

Native reference: `g2/build/c-firmware/20261011/em-inspection-full.arcem.txt`,
image base `0x302400`, stock SHA-256
`0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03`.

The 32b61c parent writes packet type `8` to record+428. Its object begins at
record+380; object+44 is record+424, the pointer to record+428. Between this
write and BL 312918 at 32b77e, direct source calls are CRC seed 318960,
selector 317ea4, time scaling 317ebc twice, and four-slot 3246c0. The latter
accesses packet+208..223, not the type byte, and queue removal 314134 changes
the queue head/tail, not the removed node. These source-local writes do not
change the packet type. Concurrent/alias mutation outside these bodies has not
been proved impossible.

For type 8, 312918 selects index 6 (312a22), reads object+40 pointee length,
clamps it to at least 64, then calls 312be4 with R1=0, R2=0, R5=0, R7=0.
Native 312be4 fixes R13=5, R14=247 and the branch threshold R1=252.
The duration-piece child 312b88 never writes R2. Therefore the 312918 exit R2
on this path is:

```
source = *(uint32_t *)(object + 40)
length = source ? max(*(uint16_t *)source, 64) : 64
if length <= 252: R2 = (int16_t)(length + 5)
else if length % 247 == 0: R2 = 257
else: R2 = (int16_t)((length % 247) + 5)
```

The original 32b61c passes this still-live R2 to the optional callback at
32b7a8. The selected C 312918 returns only R0, so a wrapper that captures
its compiler-generated R2 does **not** establish original R2 equivalence.
An admissible source path needs a typed R2 output produced from the same native
length read inside 312918 (or a complete named-ISA lowering of that call path)
and an ARC indirect-call wrapper that restores it into R2. A second volatile
length read would change the native read contract.

## Full entry path census

The prepared typed 312918 body carries incoming R2 through paths where native
does not assign it. Its exit-R2 assignments derive from the following native
instructions. This is a register contract; the selected ordinary C provider
does not expose these results.

| Packet type | Native exit R2 source |
| --- | --- |
| invalid, 4, 5 | Incoming ambient R2; the index branch does not set R2. |
| 2 | Incoming R2 if packet+104 is zero; otherwise byte packet+149 loaded at 312966. |
| 3 | Word packet+104 loaded at 3129bc if zero; if nonzero, 0xc10 at 3129ca, then byte packet+149 at 3129ea when packet+108 is nonzero. |
| 6 | Nonextended and packet+100 zero retains incoming R2; nonextended active gets byte packet+124 at 312b52. Extended always gets 36 from the 312a9c branch delay. Extended active with kind other than 3 overwrites it with 400 at 312abc. |
| 7 | Initially 13 from the 312a54 branch delay. The final amount path overwrites it: amount at most limit yields sign-extended low16(amount + max(packet+100 halfword,13)); amount above limit yields full 32-bit remainder when its low16 is zero, or sign-extended low16(remainder+13) otherwise. |
| 8 | Size/247 formula above from 312be4's R2. |
| 9 | 5 from 312be4 with size zero. |

Child 312b88 reads R2 for its own duration calculation and does not write it.
The selected 312be4 C return models R0; its internal R2 is reconstructed in
the typed caller for types 8 and 9. The prepared alternative canonical entry
passes native incoming R2 to the typed body and restores its exit R2. This
still requires independent review of callers that might observe R1/R3 or
other live register effects and any concurrent mutation of type 8's packet.

## Direct caller register census (full native listing)

The full listing contains ten direct `BL 312918` sites: `31c862`, `322064`,
`327dac`, `327f0a`, `328284`, `328546`, `32a9aa`, `32ad06`, `32b3a2`, and
`32b77e`. The first eight do not read a live 312918 result before either
overwriting the relevant argument registers, calling another function, or
returning. The latter two enter optional indirect callbacks before another
call, at `32b3d6` and `32b7a8` respectively. The `32b77e` caller has no
instruction that sets `R2` between the `3246c0` return and `BL 312918`;
the experiment's `incoming_r2` parameter is therefore only a controlled
input, not the canonical one-argument parent's ambient register contract.

The callbacks may also inspect `R3`. Native 312918 uses `R3` as its duration
accumulator and leaves it live after storing object+12. Its type-8 child
`312be4` is followed by `MOV R3,R0` at `312a8e`; thus the type-8 312918
exit `R3` is the returned duration. Neither parent callback path explicitly
overwrites `R3` before the indirect call. The prepared typed body now exposes
`R3` from the original computed duration at the store, and its alternative
entry and optional-call wrappers restore `R2/R3`. This avoids a new volatile
read. `R4-R7` and any other ambient callback registers remain unqualified.
For the type-8 branch, native `312a7a..312a8e` passes `R4=size`, `R5=0`,
`R6=packet+14 mode`, and `R7=0` into `312be4`. That child saves `R13-R15`,
does not write `R4-R7`, and its `312b88` child only uses `R0-R2`.
Consequently these four registers are still live at the parent optional
callback, but the prepared callback wrapper does not restore them. Any
selection needs a named register transport or a proved callback signature.

The prepared entry shim is a *replacement* for the selected ordinary C
`312918` definition, never a second definition. The shim's `R2` input is
captured at actual entry and its `R2/R3` output is reloaded after the typed
helper call. Target compile/link, disassembly of the shim and all callers,
volatile read trace, callback `R1-R7` behavior, and packet-type mutation
assumptions remain independent admission gates. These gates are open; this
crosswalk does not claim binary, runtime, or hardware equivalence.

## Full native ABI alternative

`../worker-object-native-abi-312918/source.c` now carries all 221 native
instructions as named ARC assembly in C, including the eight four-byte BI
jump-table entries and the warned MPYWHL at 3129f6. Its 12 BL relocations
name four genuine source children. The pinned target compiler accepts it;
`../worker-object-native-abi-312918/target/receipt.json` records the
instruction and jump-table crosswalk. Four ambiguous short SUB/ASL encodings
are expressed as baseline full instructions, yielding a 630-byte compiled
body against the 622-byte native body. This candidate is prepared only and
supersedes the typed side-channel as the preferred canonical replacement
for native register ABI preservation. Parent optional callback transport and
whole-image placement/equality remain separate gates.

`init_associated_cycle_ambient_r2.c` now contains the parent bridge for the
preferred full native body: `3246c0` then canonical `312918` in one ARC
wrapper, immediate R2-R7 snapshot, and an optional callback wrapper that
reloads R0/R1/R2-R7 before `JL_S`, then executes native `MOV R2,R0` after
callback return. `associated-regs-target/receipt.json` records target
disassembly and a four-route host fixture with six distinct register
canaries. The fixture validates C routing with stubbed ARC wrappers; it does
not execute target instructions. Packet type 8 is written before `3246c0`,
but mutation to an unexpected type before `312918` would expose ambient
entry registers from the selected C `3246c0` implementation rather than
stock scratch values. The callback's use of R8-R12 is also unqualified.
The parent source reads record+798 before storing the second 317ebc result,
then writes record+656 before calling the combined bridge. Native 32b76c
loads that byte, 32b76e stores the second result, and the 32b774 `BL.D
3246c0` delay slot at 32b778 writes the captured byte to record+656 before
the child executes. This ordering matches the prepared C call boundary for
single-threaded memory effects; interrupt/alias observations need separate
review. The optional wrapper uses R12 as its snapshot pointer, whereas
native makes no R12 write between 312918 return and optional `JL_S`.
Because no accepted producer/signature for the pointer at 0x801a14 is known,
the prepared parent is not a complete ambient callback ABI replacement.
