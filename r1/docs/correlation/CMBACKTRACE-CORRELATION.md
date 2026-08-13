# R1 CmBacktrace provider correlation

## Result

The R1 crash-diagnostic core is attributable to Armink's MIT-licensed CmBacktrace source. The
recovered image does not prove one exact vendor checkout, but it does prove an unmodified-upstream
compatibility interval from commit `4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c` through
`73714489f9d8af130aacb515586b397b604a5768`. The latter is the newest compatible state and is the
authenticated reproducibility baseline already stored at
`../../g2/third_party/cmbacktrace`. It declares
CmBacktrace 1.4.2; it is not represented as the exact Even Realities checkout.

Two version boundaries establish the interval:

- recovered `dump_stack` at `0x0005CD14` limits output to 16 words. That bounded dump behavior first
  appears at `4abadfa0`;
- recovered `cm_backtrace_fault` at `0x000585BC` advances past the basic and optional FPU exception
  frames and immediately checks stack bounds. It does not apply the stacked-xPSR bit-9 alignment
  adjustment introduced by `55e7b6990640c481e83ae8a3c0f3af2092b9f7a6`, making the immediately
  preceding compatible state `73714489` the upper bound.

An Even-maintained fork inside that interval remains possible. The source-admission decision is
therefore “authenticated compatible provider plus bounded R1 adapter,” not “byte-identical vendor
checkout.”

## Recovered configuration

| Setting | R1 value | Address evidence |
| --- | --- | --- |
| OS | FreeRTOS | current-task stack/name adapters at `0x0006A098` and `0x0006A0B0` |
| CPU | Cortex-M4 with FPU exception-frame handling | `cm_backtrace_fault` at `0x000585BC` |
| Toolchain | GCC | linked Cortex-M Thumb exception-entry form and ELF diagnostics |
| Language | English | recovered fault-diagnosis strings |
| `CMB_NAME_MAX` | 20 | three 20-byte copies in `cm_backtrace_init` at `0x000588A4` |
| `CMB_CALL_STACK_MAX_DEPTH` | 32 | 32-entry scan/format path at `0x00081918` |
| `CMB_DUMP_STACK_DEPTH_SIZE` | 16 | bounded loop at `0x0005CD14` |
| stack dump | enabled | fault path calls `dump_stack` |

The stock initializer receives the long product build path, hardware string `603MV1.9.3`, and
software string `2.2.6.0009` from application startup `0x00075F64`. The open build deliberately
uses `r1` as its firmware name while retaining the two recovered compatibility strings.

## Function ownership split

The following bodies correlate directly to upstream source and must be compiled from the
authenticated provider snapshot:

| R1 entry | Upstream symbol |
| --- | --- |
| `0x0002746A` | `cmb_get_psp` |
| `0x00027470` | `cmb_get_sp` |
| `0x000584F0` | `cm_backtrace_call_stack_any` |
| `0x000588A4` | `cm_backtrace_init` |
| `0x0005C568` | `disassembly_ins_is_bl_blx` |
| `0x0005CD14` | `dump_stack` |
| `0x000634CC` | `fault_diagnosis` |

The two machine accessors are exact GCC forms from provider `cmb_def.h`: `MRS r0, psp; BX lr` and
`MOV r0, sp; BX lr`. Their complete bodies are byte-pinned independently. The functions at
`0x000585BC` and `0x00081918` retain upstream fault/unwind structure but add R1
build-time, watchdog, fault-time, and output-format behavior. Entries `0x0006A098` and
`0x0006A0B0` provide the product FreeRTOS name/stack seams. The latter uses four non-upstream,
byte-pinned TCB accessors: saved SP at `0x00096138`, used stack words at `0x0009613C`, current-task
stack base at `0x000964B0`, and current-task stack depth at `0x000964BC`. These are bounded R1
adapter behavior, not FreeRTOS provider bodies. Five consecutive exception entries at
`0x000274AC`, `0x000274B8`, `0x000274C4`, `0x000274D0`, and `0x000274DC` pass LR and SP into the
provider. These are classified as R1 provider adapters; they are not claimed as pristine Armink
source.

## openR1 integration

The Nordic image now compiles the authenticated `cm_backtrace.c` directly. Local code is limited
to:

- the recovered Cortex-M4/FreeRTOS/English/depth configuration;
- statically allocated R1, idle, and timer task stacks and public stack-bound accessors, avoiding
  modifications to or private-layout reads from FreeRTOS TCBs;
- exception-entry glue that passes LR/SP to `cm_backtrace_fault`;
- linker-name adaptation for the application stack/code range; and
- a bounded 2 KiB `NOLOAD` retained diagnostic sink. It is not exposed over unauthenticated BLE;
  a future diagnostic transport must apply an explicit authorization policy.

The provider snapshot has its own offline commit/tree/source/license verifier. The openR1 vendor
audit runs that verifier, checks the exact core-source hash, and the linked-image verifier requires
the provider and port symbols.
