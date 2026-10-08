# ILO prevention lock: target DeepSleep callback and registration

**342 new original/independent/public comparisons PASS**: 336 direct callback cases, four actual registration/dispatcher compositions and two cancellation/start/stop sequences. Independent [pm.c](../../components/touch/ilo_pm_offline/pm.c) reconstructs0xa1c0; selected verbatim pinned PDL Cy_SysClk_DeepSleepCallback compiles with explicit target types/statuses and EXCO/WCO disabled. Those feature macros are absent from the selected CY8C4046FNI_T412 device header; stock has no corresponding clock-transition bodies. No function-entry stubs.

```c
CHECK_READY(1): if (measuring) return FAIL; prevent = true; return SUCCESS;
CHECK_FAIL(2): prevent = false; return SUCCESS;
BEFORE_TRANSITION(4): return SUCCESS;
AFTER_TRANSITION(8): prevent = false; return SUCCESS;
other: return FAIL;
```

FAIL=0x4200ff, SUCCESS=0. Params are unused, including null/invalid pointer tests; no dereference occurs. Readiness failure retains the existing prevention byte. Before transition leaves it unchanged. Noncanonical nonzero bool bytes are tested synthetically.

## Actual project registration and call chain

Authenticated reset data ROMb91c stores Thumb pointera1c1. The reset-copy241-word blockb58c→200004c0 places it at descriptor20000850. Descriptor typebyte+4=1(DeepSleep), skipmodeu32+8=0, params+12=20000ccc, links+16/+20=0 and orderbyte+24=0xff. Registration wrapper4634 loads descriptor from literal4648 and calls actual RegisterCallbacka3b0 at4638; true becomes wrapperreturn0, false becomes0x4200ff. Four tests use that actual descriptor/wrapper and actual dispatcher a444 for phases1/4/8, replacing only the descriptor's function pointer with original/native/public callback respectively. All persistent SRAM except that necessarily differing pointer is compared. The actual DeepSleep root20000f38 contains the descriptor after registration. Only this callback is registered in these tests, not the entire startup list.

Actual dispatcher calls function pointer via BLX at a4ba for forward phases and a512 for reverse traversal. Observed callback phase traces in results.json retain exact registration and delivery evidence. Direct cancellation sequences use actual Start9d90 and Stop9ddc to confirm CHECK_READY blocks new measurement until CHECK_FAIL releases it. Explicit phase calls are synthetic scheduling, not physical sleep/wake or concurrent ownership evidence.

## Remaining boundary

This closes the previously unestablished **callback body and descriptor/registration path**, not whole-startup registration ordering or wake timing. Prior application sleep tests used empty callback roots; they must not be retrospectively treated as tests of this installed callback. The dispatcher and registration are executed original dependencies here, not independently source-reconstructed functions. Pinned PDL source provides the next actionable source lead for those bodies. Full physical sleep/wake requires a device trace or faithful peripheral/interrupt model; this batch makes no patch-safety claim.

Reproduce: build_offline.py --gcc <ArmGNU13.3> --pdl-source <pinned cy_sysclk.c> --output <scratch>, then venv python verify.py <scratch/pm.elf>. Reproduction receipt pins source, explicit public environment, compiler and ELF. No firmware/index/commit/device writes.
