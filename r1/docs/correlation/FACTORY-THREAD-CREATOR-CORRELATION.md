# Factory-input thread creator correlation

The Ghidra-omitted creator at `0x00045C54..<0x00045C84` is now a 48-byte manual
provenance supplement with SHA-256
`d85c228dacba440caeda739336298761c7a52619589196c7801535254c8255dc`.
It calls CMSIS `osThreadNew` once at `0x00045C5C`, stores the returned handle at offset 8 of
state block `0x200066B0`, and enters the stock fail-stop boundary if that handle is null.

The three literal words select attributes `0x000992D0`, odd factory-input task entry
`0x0009230D`, and state block `0x200066B0`. The nine-word CMSIS attribute record names the task
`"factory_test"`, requests an 8,192-byte dynamically allocated stack, preserves raw priority 39
and TrustZone module 1, and leaves attribute bits, control-block memory, and stack memory null.
The decompressed scatter state independently binds odd create pointer `0x00045C55` and stop
pointer `0x00045C3D`.

`r1_factory_input_thread_creation_plan_build` records these immutable creation parameters and
the null-result policy. It does not call CMSIS, allocate a stack, expose a function pointer, or
start a task. The already source-gated entry body remains represented by
`r1_factory_input_task_plan_startup` and `r1_factory_input_task_plan_flags`.

`python3 tools/evidence/summarize_r1_factory_thread_creator.py` validates the exact body, sole
CMSIS call, literals, attribute words/name, and scatter registration against the rebuilt image.
