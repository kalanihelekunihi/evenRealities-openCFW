# CASE fixed-catalogue entries without header address leads

This review records the 20 entries isolated in the first no-header pass;
`0x08005f44` now has its own source file and header lead. A semantic match below is a
source lead, not proof of whole-body equivalence. The direct-BL audit now has
zero unmentioned targets, but indirect callbacks and uncalled functions need
their own body and state comparisons.

| Native entry | Current source lead | Qualification |
| --- | --- | --- |
| `0x08000156` | `startup_vector_candidate.c` `case_vector_default_0156` | Infinite-loop handler source; placement unproved. |
| `0x080002d6` | `startup_vector_candidate.c` `case_crt_decode_02d6` | Decoder native/C output PASS420 on authenticated compressed stream; typed CRT state separately PASS420. |
| `0x080006c4` | `startup_handler_forward_candidates.c` `case_vector_irq_06c4` | Vector forwarding cut original/C PASS4 integrated suite. |
| `0x08002f28` | `owned_lower_aliases_candidate.c` `case_init_usb_reset_requested` | One-byte sensor selector `0xa2`; self-check chain original/C PASS10, hardware read remains physical. |
| `0x08003a30` | `owned_lower_aliases_candidate.c` `case_init_sensor_prepare` | RAM state clear sequence; original/C PASS8. |
| `0x08005f44` | `application_boot_sensor_flags_candidate.c` `case_boot_sensor_flags_5f44` | Two sensor status words ORed; original/C PASS256. |
| `0x08006778` | `startup_vector_candidate.c` `case_vector_hardfault_6778` | Infinite-loop handler source. |
| `0x08006d70` | `startup_vector_candidate.c` `case_vector_nmi_6d70` | Infinite-loop handler source. |
| `0x08006e08` | `startup_handler_forward_candidates.c` `case_vector_irq_6e08` | Vector forwarding cut original/C PASS4 integrated suite. |
| `0x08006e18` | `startup_vector_candidate.c` `case_vector_svc_6e18` | Empty handler source. |
| `0x080084ae` | `startup_vector_candidate.c` `case_early_hook_84ae` | Empty startup hook source. |
| `0x080084b0` | `startup_handler_forward_candidates.c` `case_vector_irq_84b0` | Vector forwarding cut original/C PASS4 integrated suite. |
| `0x08008f98` | `startup_handler_forward_candidates.c` `case_vector_irq_8f98` | Vector forwarding cut original/C PASS4 integrated suite. |
| `0x0800ba64` | `bus_response_sample_candidate.c` `case_bus_input_line_prepare` | GPIO input-mode operation composed into response sample; enclosing native/C PASS15. |
| `0x0800ba84` | `bus_positive_waveform_candidate.c` inline `configure` | Positive-channel output-mode operation; enclosing waveform PASS24. |
| `0x0800bac4` | `bus_positive_waveform_candidate.c` inline `high` | Positive-channel pin high; enclosing waveform PASS24. |
| `0x0800bae8` | `bus_positive_waveform_candidate.c` inline `low` | Positive-channel pin low; enclosing waveform PASS24. |
| `0x0800bb0c` | `bus_positive_sample_candidate.c` inline `configure(state,2,1)` | Positive-channel input-mode operation; enclosing sample PASS12. |
| `0x0800bf08` | `application_policy_ota_side_prepare_candidate.c` `case_policy_ota_right_finish` | Four sourced sensor commands; side/box native cut oracles PASS8/PASS12. |
| `0x0800c3f8` | `application_init_bus_output_sample_candidate.c` `case_bus_output_parity` | Delegates to independently sourced parity routine; parity oracle PASS259. |

The separate indirect callback `0x080086e0` was absent from those mappings.
It now has `application_boot_sensor_cancel_callback_candidate.c` and passes
128 original/C register and RAM comparisons. The other rows remain semantic
source leads until relevant whole-body checks establish equivalence.

An aligned Thumb-pointer census of the authenticated payload finds 39 distinct
code-pointer candidates, including 15 absent from both fixed pseudocode entries
and direct BL targets. All 15 have source address leads, but a lead alone did
not establish callback coverage: native `0x0800bf8c` was missing as an actual C
entry. `event_set_callback_candidate.c` now forwards the event pointer and bits
to the task-context event-set provider; `verify_case_event_set_callback.py`
checks 256 stock/C ABI call pairs split between the native clear and set
callbacks. Existing indirect-entry iteration checks
also pass for the transport monitor (192), timer-service task (64), and policy
task entry/iterations (168). The pointer scan excludes runtime-constructed
pointers and may contain coincidental literals, so it is a bounded census.

The formatter at `0x08009210` has one native direct BL caller, the logger
wrapper at `0x08009170`. `verify_case_logger_consumer_abi.py` checks 128
stock/C varargs frames (five argument words, format, context and output
callback handoff) at that call boundary. `verify_vformat_basic.py` separately
checks 815 bounded formatter cases, including authenticated caller literals.
Neither check proves the downstream UART hardware write.

Further integrated-ELF indirect entry checks: `verify_case_idle_task_entry.py`
compares 256 two-iteration `0x0800ae5c` maintenance/reschedule traces over the
ready-count boundary; `verify_case_transport_trampoline.py` compares 256
`0x08008558` context lookup and null/present indirect callback paths. The
transport confirmation callback at `0x0800bb90` also passes 256 integrated
state, child-call, log-format-address, and RAM comparisons; its earlier
isolated oracle covers 768 cases. These establish bounded transitions. The
nonreturning policy task, startup entry, UART physical output and task fault
path still need separate whole-body/layout/hardware qualification.

`verify_case_log_output_char.py` now checks 256 integrated stock/C calls at
indirect formatter emitter `0x0800a380`: UART handle, byte, length, timeout,
and original 32-bit character return agree after cutting the UART lower. This
qualifies the callback's source semantics; physical UART output is untested.

Startup `0x080000b8` passes 128 stock/C cut-path comparisons: the new SP and
CRT R0 are `0x20002c88`, followed by the application entry after the CRT
returns (`verify_case_startup_entry_00b8.py`). The test cuts the CRT, so its
data initialization is supported separately by the 420-byte decode/default
checks. Task-return fault `0x0800b31c` originally compiled both stock fatal
lanes into one loop. Its C source now preserves the native overflow/ordinary
branch, and the first 16 compiled instruction bytes match stock exactly;
`verify_case_task_return_fault.py` checks five depth values, both loop PCs,
PRIMASK disabled, and unchanged RAM. This is native nonreturn behavior.

The policy task at `0x08007200` still has a whole-entry gap. Native body
branches at `0x77ae`, `0x77cc`, and `0x7e94` can enter the `0x7eda` 1000-tick
wait; `0x7ed6` then calls back into `0x7214`. An instruction trace follows
three `0x7214` entries: SP stays `0x20007fc0` and LR changes from initial
`0x20001001` to `0x08007edb` on the recursive call. The source iteration's
own wait represents this tail wait; an additional outer wait would double it.
`verify_case_policy_reentry_two_turns.py` compares two full stock/C turns over
eight idle/service conditions, including child calls, RAM, and tick state.
Other branches and unbounded continuation remain outside this proof.
