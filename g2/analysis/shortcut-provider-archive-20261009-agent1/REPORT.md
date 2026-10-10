# NationalChip provider/archive frontier continuation

Status: ready for independent review as dependency evidence. This is a private
P2 source-identification attempt, with no canonical coverage or gate admission.

## Inputs and reproducible scope

`inventory.py` parses ELF32 sections, symbols and REL records from eleven members
of pinned NationalChip `libdriver_release_v1.0.6.a`: audio input/output, I2S,
SNPU hardware/MCU/register/core, PMU control/oscillator, clock, and device.
`archive-inventory.json` records the archive hash and complete executable-section
inventory; `function-inventory.json` records symbol sizes, individual candidates,
relocations and branch-target checks. Native archive listings and full native
stock XIP/SRAM listings are retained beside them. The public dependency is
`third-party/upstream/nationalchip-lvp-kws` at
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`.

XIP SHA-256 is rechecked as
`49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584`.
The prior conditional mappings are XIP `0x10203004` and SRAM `0x10023400`;
this report does not add hardware mapping proof. The new script records SRAM's
actual hash, and the existing campaign ancestry remains the prerequisite for
admission. It never changes either input.

121 executable archive sections and 175 sized function symbols were enumerated.
44 sections have XIP candidates equal outside explicit relocations. Function
comparison across XIP and SRAM yields 82 symbols with at least one candidate
that has no contradicted known branch target, including 34 exact function-byte
matches. Their aggregate symbol size is 8,200 bytes. This aggregate is neither
unique code coverage nor newly decompiled bytes; section/function extents can
overlap and include pools. Section candidates total 4,054 bytes, also not an
additional denominator. Tiny functions below an eight-byte stable anchor and
functions whose LRW layout differs deliberately remain unmatched here.

Only ELF relocation types 1 (`R_CKCORE_ADDR32`) and 19
(`R_CKCORE_PCREL_IMM26BY2`) occur in this scope. Each masks exactly its recorded
four bytes; no other instruction or pool-layout difference is silently ignored.
Masked equality is a candidate identification, not exact linked equality.
All stock BSR targets are independently decoded by GNU objdump. A target is
confirmed only when the expected symbol has a candidate at that address;
unresolved targets stay explicit. ADDR32 records preserve original and linked
words and their inferred symbol-base difference, without claiming all dynamic
or data identity obligations are closed.

## Useful positive providers

| Provider | Conditional stock entry | Evidence |
| --- | --- | --- |
| `_ain_reset` | `0x10203c88` | Entire 320-byte section exact; prior audio-exit/reset boundary can now be attributed directly. |
| `_pcm_channel_setting.isra.0` | `0x10203dc8` | Entire 78-byte section exact. |
| `gx_audio_in_set_input_sadc/pdm/i2s` | `0x10203e18`, `0x10203e7c`, `0x10203ec8` | 100/76/168-byte sections equal outside named call and BSS relocations. |
| `gx_audio_in_set_input_channel` | `0x10203f70` | Entire 54-byte section exact. |
| `gx_audio_in_set_dc_enable`, `set_rough_gain`, `set_evad_enable`, `set_evad_threshold` | `0x10204350`, `0x102043ac`, `0x102043fc`, `0x102044e0` | Entire 90/80/228/76-byte sections exact. |
| `gx_audio_in_set_logfbank_enable`, `set_fftvad_enable` | `0x1020452c`, `0x10204570` | Entire 66/132-byte sections exact. |
| FFTVAD curve/chipping/state helpers | `0x102045f4..0x102047b8` | Individually exact archive sections in the JSON inventory; ranges contain alignment and are not one body. |
| `gx_audio_in_init` | `0x102047e4` | 416-byte section equal outside four call and two ADDR32 relocations. `_ain_reset` and clock-enable call targets are independently corroborated. |
| `reg_get_bit`, `reg_set_bit`, `reg_clr_bit` | `0x102055c0`, `0x102055cc`, `0x102055dc` | Exact 10/14/16-byte function extents. |
| `npu_en_interrupt` | `0x1020566c` | 120-byte function equal outside seven BSR relocations, all linked calls confirmed as `reg_set_bit`. |
| `gx_pmu_ctrl_set` | `0x10025d74` | 206-byte function equal outside explicit relocations. |
| `gx_pmu_ctrl_get`, `gx_pmu_ctrl_enable` | `0x10024810`, `0x100248cc` | 184/112-byte function candidates equal outside explicit relocations. |
| `gx_clock_set_module_enable` | `0x10025080` | 256-byte function candidate plus explicit native linked-target evidence. |

The audio BSS relocation base inferred consistently by input-SADC and init is
`0x20027330`. Audio init's ISR section relocation points to `0x10025e48`.
These are concrete future typing/link-map seeds, not hardware behavior proof.

### A masked-match false positive was rejected

`npu_dis_interrupt` also initially matches `0x1020566c` when its seven call words
are omitted. Its archive expects `reg_clr_bit`, at `0x102055dc`; stock instead
calls `reg_set_bit`, at `0x102055cc`, at all seven sites. The candidate is marked
`branch_relocation_contradiction: true` and excluded from the 82-symbol count.
This demonstrates why masking call words alone cannot establish provider
identity, especially for paired set/clear wrappers.

## Public source and ABI constraints at exposed roots

Public `include/driver/gx_audio_in.h` selects the v2 header for GRUS;
`gx_audio_in_v2.h:750` declares five callbacks in this order: record, config,
update, energy-VAD, FFTVAD. `gx_audio_in_init` takes that structure by value.
Archive instructions save r0/r1/r2/r3 and load the fifth word from the caller
stack. They call the config callback synchronously and register IRQ2; the ISR
and transitive configuration effects remain separate review obligations.

Stock lifecycle root `0x102073bc` agrees with public
`lvp/common/lvp_audio_in.c:597`: clear a 20-byte control structure; pass record
`0x10026214`, config `0x10207234`, update `0x10207020`, r3=0, and a zero stack
word; call archive-identified `0x102047e4`; save the supplied caller callback.
The last two callback slots are therefore null on this initializer path. There
is no optional DMIC clock-source call on this path. This constrains the selected
conditional source branches without proving the entire global configuration.

Public `gx_snpu.h` has incompatible LEO and GRUS APIs: LEO has a six-pointer
task and one-argument run entry, while GRUS has module_id plus seven pointers
and three-argument asynchronous run. The registered archive's GRUS object paths
and audio-v2 interface constrain the applicable provider ABI. Do not import
the LEO callback signature into the G2 project.

Public `lvp/common/lvp_pmu.c:172` constrains the suspend root `0x10207808`:
save IRQ state; reject retained suspend locks; invoke registered callbacks;
restore IRQ state; suspend audio; poll NPU state until it differs from BUSY=1;
exit SNPU; set wake mask and SRAM wake address; disable interrupts; optionally
enable FFTVAD-start IRQ; enter PMU control. Stock independently shows PMU command
3 and command5, the archive-identified setter `0x10025d74`, wake-from byte1,
resume address `0x10023500`, and PMU-enable `0x100248cc`. The public header assigns
GPIO=1, RTC=2, audio=4 and I2C=8: the already observed TWS request13 is therefore
GPIO|audio|I2C under this API. This source-defined mask is not proof that those
external wake mechanisms function on hardware.

The archive's six-byte `gx_snpu_get_state` uses LRW plus load and return. Stock
PMU polling invokes `0x10205e28`; native stock resolves its LRW through a moved
pool. That short/layout-sensitive body is outside the stable-anchor matches,
so its identity remains source/native correlation rather than exact equality.

## Precise remaining boundary

Public lifecycle C, driver headers, named archive symbol tables and relocation
graphs are available. The private implementation begins inside audio-v2,
GRUS SNPU core/register/MCU operators, PMU and clock driver object code: their
registered paths contain `.o` providers, not corresponding implementation C.
The archive gives concrete object boundaries and symbols but cannot be retained
as executable implementation to satisfy the final complete-from-source target.

Unmatched archive functions remain explicit, chiefly pooled SNPU core and
layout-sensitive register helpers, IRQ/audio callback internals and I2S variants.
Resolving them requires semantic firmware/archive review with pool and callback
accounting, not another source download. Model command/weight generation,
retained-state dispatch, volatile ordering, transitive external effects and
hardware mapping remain open. No global exhaustion claim follows from a finite
eleven-object inventory. No additional source was identified that justifies a
new download/submodule; the useful provider is already pinned.

No Ghidra export was needed to identify these sections: native ELF metadata and
GNU objdump give the relevant independent oracle. Ablation/REA still have the
previously documented C-SKY support boundary. Validation ran the reproducible
script, parsed all generated JSON and checked scoped whitespace. No canonical
ledger, firmware sources, installed processors, submodule pins or gates changed.
