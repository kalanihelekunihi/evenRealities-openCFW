# R1 EAT command dispatch in C, 2026-11-11

`r1/src/application/runtime/native_eat_tx_registry.c` now owns stock EAT
command dispatch `0x4f6f8`, asynchronous enqueue `0x3d7cc`, and its task body
`0x44ea0`. Dispatch reads the mutable registry, rejects disabled or long
commands, compares the input prefix against each table entry, checks the
entry flags, and calls synchronous handlers or schedules asynchronous ones.
The task body calls the handler, frees its 8-byte context, and deletes the
current task. Stock schedules an `AT` task with 1,024 stack words and
priority two; the C call uses the existing source-owned FreeRTOS constructor.

The ignored probes under `build/r1-eat-dispatch-20261111/` ran 700 paired
stock/C dispatcher cases and 300 cases each for enqueue and task execution.
They compared calls, arguments, mutable registry bytes, and job context
bytes; all 1,300 pairs matched. A probe rejected an initial 512-word/`EAT`
task setting, which was corrected before the final runs. The actual manifest
object and the object used for the final probes have identical SHA-256
`fdd2c956dd9f9efeeb6ab53c6d615a9e9254d101b754a81a0f62d0cdc73ca6a3`.
The probes model allocation, task creation, callback execution and task
deletion; they do not validate scheduling or physical console behavior.

`./make.sh sources-check` passes with 985 R1 units, 772 source files and no
unbuilt R1 units. The full source build compiles 903 application and 82
bootloader units with no duplicate strong symbols. The strict bootloader
link and C vector pass. The strict application link has 15 undefined
functions and uses 628,704 of 696,320 available flash bytes. Receipts:

- `build/sources-r1-eat-dispatch-final-20261111/report.json`
- `build/r1-link-eat-dispatch-final-20261111/report.json`
- `build/r1-boot-link-eat-dispatch-final-20261111/report.json`

The source binding removes `r1_eat_command_dispatch` without adding a new
link import. At this checkpoint, the 37-entry stock table at
`0xc419c..0xc43ec` and its callbacks still needed source ownership. The
subsequent [table and initializer review](eat-core-table-c-review.md)
records the newly exposed callback dependencies. This work is neither a
complete C firmware nor stock byte identity.
