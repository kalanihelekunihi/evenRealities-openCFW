# R1 control extraction and half-position expansion in C

`native_gomore_control_extract.c` implements `0x56dc0` with its native eight-word
ABI. `native_gomore_half_positions.c` implements half-position expansion `0x67c30`
and linear progression fill `0x641c4`. The guarded generic APIs retain their
behavior under `_checked` names. No inline assembly or persistent RAM is added.

The control extractor preserves initial primary/secondary writes, the private
80-byte clear, live state-count reloads, next-position-before-current reads,
encoded-double strict spacing bounds, mode-one interval conversion, and the
alternate difference/scale selection. It reloads native period and amplitude
fields at their original use sites. The required retained count uses the native
signaling positivity test, 500/period, soft-double multiplication by 0.7 and
encoded carry. The existing peak-matcher review proves the same carry expression
against native `0x27f0c`; direct extraction cases cover its use here. Expansion
failure resets outputs and returns zero; insufficient controls return one;
otherwise the feature reducer receives the expanded data and output pointers.

Expansion reads the first halfword even with zero count, rounds half positions
through the native binary32 promotion/round/double-to-word sequence, and fills
the prefix before processing segments. Each segment captures current/next
positions, reads the next value before the previous, computes the slope before
checking capacity and signed span, then reloads its starting value. Zero or
negative span fails after the native intermediate work. The final fill reloads
the last value; zero-count wrapped addressing is retained. Fill uses a signed
exclusive bound and independently computes initial + offset*step with nonfused
arithmetic; it does not accumulate a recurrence. The raw fill returns its
original destination pointer. These are raw native contracts, without invented
empty-input guards.

Verification of the final production objects includes:

- **1,500 fill pairs and 1,805 expansion pairs**, plus **three fault pairs**, against
  stock, using raw floats, NaNs, signed zeros, rounding/FZ/DN settings, repeated or
  reversed positions, count/capacity boundaries and overlapping buffers. Results,
  ordered external writes, full FPSCR, completion, SP and preserved general/FP
  registers agree. The fill-call arguments in expansion also agree.
- **420 control-extractor pairs**, including 230 successful returns, plus **four
  faults and four incoming stack-argument alias cases**. Actual native expansion
  and feature-reducer entry counts agree with C expansion/control on the other
  side: 233 expansion and 223 reducer entries including alias cases. Private
  position-array contents and public provider arguments agree; private pointer
  addresses are normalized to contents for this direct fixture.
- Another **420 control pairs**, the same faults and aliases, with a reducer model
  that writes outputs and clobbers caller-saved general/FP registers.
- **112 actual optical-root pairs**, with 16 C control, 16 C expansion and 32 C fill
  calls. The full preexisting call trace, including nested extrema stack pointers,
  state, ordered writes, return and FPSCR agrees with stock.

Thirteen compiled defects are rejected: wrong half scaling, accepted zero span,
reversed slope, wrong slope divisor, rejected equal capacity, wrong tail value,
wrong fill index, wrong control lower/upper bounds, wrong mode, reversed
difference, wrong required-count scale and reversed output-write order.

The C control frame initially measured 160 bytes versus native 176 and shifted
native reducer-owned count pointers. A 16-byte volatile frame reservation with
one private zero write restores the native 176-byte provider depth; the strict
optical-root trace then passes without pointer normalization. Private array
placement is still different. Expansion's own frame is 56 bytes versus native
48, as observed at round calls. Private stack writes are excluded. Instruction
identity, all private addresses and hardware bus/alignment behavior are not
claimed. Counts exercised for control extraction are 0 through 41, with no more
than 40 retained entries; larger native private-array use is not established safe.

Fixtures execute native round, soft-double primitives and the feature reducer;
the normal build resolves the already-existing math providers. The feature
reducer at `0x68840` remains the explicit unresolved symbol
`r1_gomore_locomotion_feature_reduce_native`. This work does not substitute a
stub or hide that dependency.

The normal build passes **702 units: 628 application and 74 bootloader**, with no
failures or duplicate strong symbols. The newly explicit reducer increases
application imports from 179 to 180; bootloader imports remain 34. All 699 prior
objects outside the renamed checked-API owner are unchanged. Scoped qualification
selects zero regions. Hybrid equality passes with 4,381 source-built executable
bytes, 641,779 stock executable bytes and 248 resource bytes; the canonical plan
is unchanged. Complete C linking, remaining numerical selectors, the optical
root, whole executable byte identity and physical validation remain open.

The [receipt](gomore-control-extract-c-review.json) binds production, REA and replay
evidence.
