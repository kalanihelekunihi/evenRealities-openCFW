# PDM microphone buffer IRQ C source route

Stock IRQ `0x309dc` now routes to the existing, unchanged pinned Nordic SDK
`nrfx_pdm.c` symbol `PDM_IRQHandler`. REA covers its 224-byte code body, literal
bindings and two 12-byte constant events. Application vector 45 contains
`0x309dd`. No firmware implementation, source unit, state owner, compiler flag or
manifest is added or changed.

Compiled assertions against the actual SDK types confirm a 24-byte control block
and all eight field offsets. The event is 12 bytes, with requested/released/error
fields at offsets 0/4/8. The fixture links the existing compiled C object with
its static state at native `0x2002c2cc`. This controlled binding is not a final
firmware-link or cold-initialization proof.

STARTED has priority over STOPPED. Starting operation requests a buffer without
releasing one and becomes running. During running operation, availability of the
next buffer releases the finished buffer, clears its slot, flips the active index
and requests a new buffer. Missing the next buffer reports overflow only when
its prior error flag is zero. STOPPED disables PDM, becomes idle, releases the
current buffers in order and resets the active index. A separate software buffer
request is serviced at the end, with its request byte cleared before the callback.
END does not participate in this IRQ's branching.

5,328 paired two-IRQ sequences pass (10,656 invocations): 4,608 base sequences
span STARTED/STOPPED/END combinations, raw event values 1/256/`0xffffffff`, all four
operation states, both active-buffer indices, null/non-null buffer combinations,
error flags and request bytes 0/1/255. Another 720 sequences change buffers,
operation/error state, active index, handler pointer, pending events or software
requests during callbacks. These include refilling a released slot and observing
fresh active-index/handler values in later processing.

Ordered MMIO reads/writes, meaningful event fields, callback-visible control state,
final driver/register memory, return callee registers, SP, masks and adjacent state
guards match. Six negative controls reject losing STARTED priority, repeating
suppressed overflow reports, releasing the wrong buffer, retaining a released
slot, retaining a software request and omitting peripheral disable.

Native callback frames are 40 bytes versus C's 32; events are at frame+0 versus
frame+4. Event padding/private addresses, live callback registers, caller-clobbered
return registers and APSR are excluded.
MMIO hooks are bounded to the PDM registers. Inputs are controlled buffer/event
state: real microphone audio, autonomous DMA and peripheral timing, physical
interrupt delivery, exception return, null handlers, corrupt indices, arbitrary
aliases/faults and concurrency remain unproven.

Qualification compiles the unit and selects no exact regions. All 590 source/object
hashes and the manifest were revalidated against the prior passing normal build,
with 164 application / 34 bootloader imports, no compile failures and no duplicate
strong symbols. Firmware C is unchanged. The retained canonical hybrid artifact
and current source-plan hash are unchanged: 4,245 source-built, 641,915 executable
fallback and 248 resource bytes. Source-built includes admitted assembly/data.
Complete source-only rebuilding and byte-identical C reconstruction are unproven.

The preceding PWM playback/stop APIs remain compile-only. A search found the PWM
control-base literal in its IRQ stub; that is a search lead, not proof that API
counterparts are absent. No new PWM API route was accepted in this pass.

Machine-readable evidence: `pdm-irq-c-review.json`. Reproducible ignored probes:
`build/goal-r1-pdm-irq-c/`.
