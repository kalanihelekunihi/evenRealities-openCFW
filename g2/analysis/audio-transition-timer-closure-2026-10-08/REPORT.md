# PCM2.2 transition and deferred completion recovery — 2026-10-08

**Seven newly reconstructed functions pass1,364 original-instruction comparisons against the exact rebuilt ELF.** This batch completes one nontrivial transition-table body (sequence2), its delayed completion2b, delayed completion7b, timer completion dispatch/stop, and deferred21b/post-LP-to-HP completion. It does not complete all27 transition-table entries or establish live IRQ timing. [Exact-build validation](exact-build-validation.json), [source](../../components/audio/transition_timer_offline/transition.c), [fixed-width interface](../../components/audio/transition_timer_offline/transition.h), [original disassembly](disassembly-evidence.txt).

## New behavior

| Original function | Comparisons | Recovered behavior |
| --- | ---: | --- |
| 0x5A22C0 sequence2 |1,024|Complete prior timed work if timer enabled; publish trim/target globals, apply TON, boost VDDC, start50us timer, mark pending sequence2 |
| 0x5A23F8 completion2b |18|Apply saved VDDC/coreLDO trims, settle5us, clear two PWRSW selectors, restore VDDF, mark invalid26 |
| 0x5A2B14 completion7b |32|Apply saved trims, settle5us, optionally switch HP→LP, adjust power-domain overrides, attempt HP restoration, mark invalid26 |
| 0x5A40CA completion dispatcher |164|Save/disable IRQs; dispatch only pending2/7; always stop timer; restore PRIMASK |
| 0x4802CE timer stop |54|Disable timer/global enable, release clock client(4,49), disable NVIC82, clear peripheral interrupts, APB flush read, clear NVIC pending |
| 0x5A3E24 completion21b |36|Read trim from current profile, update coreLDO/VDDC, clear continuation flag |
| 0x5A40B6 post-LP-to-HP |36|Run21b only when continuation flag is nonzero; return0 |

### Sequence2 is two phases, not immediate settled completion

```c
sequence2(next, old, ton, old_ton) {
    read_next_and_old_trim_fields();
    if (timer15_enabled) {
        for (i = 0; i < 60 && !timer15_compare0_pending; ++i)
            delay_us(1);
        boost_completion(); // Also called if the status never appeared.
    }
    publish_pending_trim_and_target_fields(next, ton);
    apply_ton(ton, next);
    VDDF_trim = INFO1_word_at_plus_0x50 & 127;
    VDDC_trim = min(127, old_VDDC + 2 * max(0, next_VDDC-old_VDDC));
    last_state_before_timer = next;
    timer_start_us(50); // Compare receives300 through stock×6 conversion.
    pending_sequence = 2;
}
```

The60-count polling bound and50 argument are original stock constants. Their intended microsecond unit is corroborated by pinned HAL; physical duration is unmeasured. When prior timer status never appears, software still calls completion after bounded polling. Tests cover immediate-status and full-bound timeout paths, but do not interpret passive MMIO as a real timer expiration. Pending state2 is written after timer start; no IRQ interleaving occurs in these fixtures, and no real race or scheduler hazard is asserted.

The timer completion entry is callable directly from transition code as well as being named an interrupt service by public HAL. It does not check a timer-pending bit itself. For pending2 or7 it completes the saved work and sets26; for tested pending0/26 it only stops the timer and preserves that byte. Stop always releases the actual clock client and clears peripheral/NVIC state. Clock-client fixtures include absent, last49, and49 with peer32 still present. This validates observable software ordering, not physical oscillator shutdown.

### Completion7b and deferred21b

Completion7b treats MCUPERFREQ low two bits=2 as HP. It requests mode1, polls ready bit2 for up to20 one-microsecond calls, changes PWRSW bits6/3/25, then attempts mode2 restoration. If the temporary clock-enable bit at40004044.5 was clear, it sets it, delays1us and calls actual status polling with `(15,40004030,01000000,01000000)`. It restores HP only if the subsequently read ready bit24 is set; it clears its temporary enable afterward. Helper return values are not propagated as a completion error. Tests cover ready/unready, preexisting/temporary enable, mode0/1/2/6 and both PRIMASK values. Passive readiness fixtures stay fixed; they do not simulate real asynchronous transitions.

21b is separate from the timer pending byte. It uses current profile at200002A0, rather than the pending target at200742E8, reads the profile's calibration word for each field, programs coreLDO/VDDC and clears continuation byte20074F77. The post wrapper tests this byte and returns0, including a no-work branch. The producer sequence21 and the real caller timing after CPU LP→HP remain next targets.

## Reusable layout and call boundaries

| Address | Recovered meaning |
| --- | --- |
| 2005665C+4+4×profile |32-bit trim word: VDDF[6:0], coreLDO active[16:7], coreLDO tempco[20:17], VDDC[27:21] |
| 200742D4 /D8 /DC /E0 |Saved new VDDC /VDDF /coreLDO active /tempco uint32 fields |
| 200742E4 /E8 |Target TON and power profile uint32 |
| 200002A0 /A4 |Current profile and last profile before starting timer |
| 20004540 |One-byte pending sequence:2,7 or invalid26; other tested states do not dispatch |
| 20074F77 |One-byte continuation flag for deferred21b |

The exported header uses `uint8_t` for pending state; the build explicitly selects `-fshort-enums`. This retains the compact-enum requirement demonstrated by the prior441-input public-leaf experiment without assuming default host ABI or whole vendor structure compatibility.

Actual shared stock code executes at delay4807A0, TON adjust5A423C, timer start480240, clock release4C4530, status poll4807FC and IRQ save473940. No successful external-call return stubs are substituted. Delay reaches the **real OTA-decompressed ITCM40 helper**, reusing the sealed authenticated startup-record decoder evidence. The prior missing-ROM40/48 conclusion remains superseded by the [callback closure correction](../audio-platform-callbacks-closure-2026-10-08/REPORT.md).

Tests compare ordered MMIO writes, actual helper call arguments, trim/target globals, clock-client bitmap, pending/continuation bytes and PRIMASK. Void callbacks do not claim a meaningful R0 success return; original optimized code sometimes leaves scratch/caller values there. Selected M33-compatible ARMv8-M/FPU emulation is not full M55 exception delivery/return. The APB flush address47FF0000 is mapped as passive synthetic data; its hardware bus synchronization effect is not emulated.

## Pinned source and remaining leads

[Ambiq HAL SDK5.1.0](https://github.com/AmbiqMicro/ambiqhal_ambiq/tree/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal) at commit `5efc0228528a8adce5eae0d226fac85d2551eb3b` provides source names, bitfield descriptions, transition macros and timer lifecycle. It is materialized at the existing registered gitlink `third-party/upstream/ambiqhal-apollo510`; project index/.gitmodules were not changed. The additional prior reference checkout remains untouched. [Pinned files and all27 candidate bindings](source-reference.json). No new submodule is necessary for this already-registered dependency.

The source is useful but differs from stock: public2b/7b specify10us where stock specifies5us; publicsequence2 computes a VDDF trim expression where this stock path uses a calibration word. Those bodies were reconstructed from stock instructions rather than substituted wholesale. Synthetic calibration words permit comparisons across zero/mixed/all-one patterns and selected profiles; authentic device trim values are still unavailable.

Remaining actionable source work is **not exhausted**: 23 nontrivial table bodies remain unvalidated in this batch, including sequence7 producer0x5A29A0 and sequence21 producer0x5A3CC6. The three no-op targets24/25/26 were executed in prior routing evidence. Next useful bounded work is completing7→7b and21→21b chains, then the remaining source-provided table bodies. Actual timer IRQ caller/dispatch integration must be traced before claiming asynchronous reachability or quiescence. No production/CFW patch is justified from synthetic scheduling alone. No device, firmware, shared campaign, commits or index were changed.
