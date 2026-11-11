# Shared R1 sensor microsecond delay and Goodix millisecond correction

The Bosch BMA delay's handwritten naked assembly body was removed from
`native_bma_interface.c`. `r1_bma_delay_us` and the Goodix dependency `delay_us`
now alias the existing `r1_twi_delay_busy` in `sdk_delay_busy.c`. C supplies the
wrapping shift and mandatory tail call. The shared implementation retains its
minimal CMP/BEQ flag primitive and register-binding constraint; this is not a
claim that all delay assembly has disappeared. One implementation serves the
equivalent native entries without an added forwarding frame.

REA confirms BMA `0x53aa4` and Nordic `0x7a72c` check the full input word for
zero, then pass its wrapping left shift by six to primitives `0x9a760` and
`0x9d3d0`, respectively. Both primitives are the same SUBS/BHI/BX countdown.
The existing typed BMA callback registration still targets its native symbol.

The ignored probe `build/goal-r1-sensor-delay-c/verify.py` passes 1,608 paired
cases across both wrappers (6,432 executions): 566 complete countdown cases
and 1,042 large-input handoff cases. It compares the entire wrapper/literal
and six-byte primitive with stock at native placements, then checks registers,
APSR flags, memory access trace, untouched stack, masks, wrapping arithmetic,
zero input and tail-call SP/LR. Large countdowns are checked to entry only.

The generated Goodix user source also corrects `Gh3x2x_BspDelayMs`: the public
demo multiplied milliseconds by 1,000 and called `delay_us` once, whereas
stock `0x2eb34` repeatedly calls the microsecond boundary with 1,000. The
generated replacement retains one call per millisecond. `Gh3x2x_BspDelayUs`
continues to forward its argument as observed at `0x2eb4a`.

`verify_bsp.py` compares both BSP entries for 20 cases, including zero, 15,
30, 1,000, 32,768 and 65,535. It executes the real microsecond wrapper and
models countdown completion to check the call sequence. A deliberate variant
restoring aggregate multiplication is rejected for two milliseconds: stock
calls 64,000 cycles twice, while the variant calls 128,000 once. This proves
the sequence distinction, not physical elapsed time. Private frames and void
return residue are excluded. The focused link reports the existing SDK-wide
versus product short-enum flag difference; these tested interfaces carry only
fixed-width integer arguments, not enums. No general enum ABI claim follows.

The normal build compiles all 564 R1 units with no failures or duplicate
strong symbols. Application imports fall from 207 to 206 by resolving
`delay_us`; bootloader imports remain 34. `make sources-check` passes.

The official qualifier selected four exact regions from the shared C unit:
two previously selected TWI wrappers and the two new 16-byte BMA/Nordic
wrappers. Only the new selections were appended to the canonical source plan;
the existing compiler arguments and selections were preserved. A fresh hybrid
build reports 3,723 source-built bytes (32 more), 642,437 retained executable
bytes and 248 resource bytes. Its application remains identical to the locked
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
[Machine evidence](sensor-delay-c-sharing-review.json) binds the REA snapshot,
execution probes, qualifier output, plan delta and hybrid report.

Physical timing/electrical behavior, complete Goodix configuration, remaining
reset/interrupt/gsensor hooks, final source-only linking and whole-image source
completeness remain unproven. Hybrid identity retains explicit executable
pull-through; G2 workflow gates are unchanged.
