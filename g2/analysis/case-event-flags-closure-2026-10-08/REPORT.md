# Case CMSIS event-flags wrapper: context, return values and source revision lead

**336 fresh PASS wrapper comparisons**, four-way original/independent/selected publicv10.3.1/v10.4.6, after rebuild. **Kernel child bodies are explicitly replaced by compiled result models** at0800c568/0800c4de on every comparator. These are wrapper instruction tests, not actual queue/scheduler integration. Registered publicv10.5.1 differs in24 selected valid ISR/existing-bit comparisons. No global SDK re-pin is justified.

[events.c](../../components/case/event_flags_offline/events.c) reconstructs0800a888..0800a8d4. Null event ID or flags with any top-eight bits returnsFFFFFFFC(osErrorParameter,-4) without kernel call. Zero flags is accepted. MRS IPSR determines thread versus ISR; PRIMASK does not change this branch. Thread delegatesxEventGroupSetBits0800c4de and returns its value. ISR initializes stack-local yield0 and callsxEventGroupSetBitsFromISR0800c568. Failure0 returnsFFFFFFFD(osErrorResource,-3); success returns requested flags. Nonzero yield triggers ICSR(e000ed04)=10000000(PendSV). A PendSV request is not proof that a task ran or bits were already applied.

## Masking and test models

Profiles supply post result0/1/2, yield0/1/2 and prior bits0/100. Inputs include IPSR0/15/16 and PRIMASK0/1. Verifier explicitly asserts restored PRIMASK equals its input on **each** comparator, and PRIMASK at each PendSV write also equals input. The wrapper preserves mask; it does not require mask1 for ICSR write. No inference about actual critical sections inside modeled kernel children is made. IPSR is preserved; invalid-argument paths make no child call.

Selected public bodies are extracted from full official hash-pinned CMSIS-FreeRTOS sources, with export names changed and explicit minimal type/macro scaffold. v10.3.1 commit677bb7fcbf38f07e106735c7c947f4efb2714b0f andv10.4.6 commit943dc0607e28d786f9b363e5da60047c1ea755d8 return requested flags after ISR success. v10.5.1 commitd213f261b5be6bb29a7cce8b84071706b72f4d53 additionally obtains existing bits. Public IS_IRQ/IRQ_Context scaffolds here use IPSR only: this does not attribute their full configuration, uniquely determine release, or prove behavior with masked thread contexts in unmodified public sources. Official URLs/full-file/body hashes and scaffold are in reproduction-receipt.json; Apache license retained.

## Dependency and practical boundary

Static original0800c568 forwards callback0800bf8d,event ID,flags,yield pointer to0800ce0c. That routine constructs command-2,callback,arg1,arg2 on stack and forwards to queue0800c7a8 through queue global20000164. Actual copy/queue state and daemon consumer are next actionable dependencies, **not proven by the336 modeled-child tests**. An app/patch must treat successful ISR set as acceptance for deferred work, not existing-bit readback or immediate completion. Queue-full/lifecycle/scheduler timing still needs concrete evidence.

Reproduce build_offline.py --gcc <ArmGNU13.3> --output <scratch>, then opencfw venv Python verify.py <scratch/events.elf>. No firmware/index/device changes, global source-completion or byte-equality claim. Original provenance/disassembly, independent source, explicit models and fresh result/receipt hashes are sealed together.
