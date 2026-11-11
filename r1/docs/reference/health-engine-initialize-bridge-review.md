# R1 health engine initialization bridge

`r1/src/application/runtime/native_health_engine_initialize.c` now binds the
firmware ABI at stock `0x6fea0` to the existing typed
`gomore_primitives_sleep_algorithm_initialize` owner. It passes the 14,816-byte
engine, 736-byte previous state, seven-float profile, timestamp, and the time
configuration at previous state `+0x298`. The adapter stores the engine pointer
in `r1_gomore_native_context` and reads the seed from the source-owned
`r1_gomore_runtime_configuration`.

The primitive now accepts optional native runtime-validation and logging
callbacks as well as the previously added native profile converter. The R1
adapter binds these to `r1_gomore_runtime_validate_native`,
`r1_gomore_log_native`, and `r1_gomore_native_engine_profile_convert`. It also
binds the native random provider, filter constructor and SPS affine-pair
helper. The primitive's generic behavior remains available when the optional
native callbacks are absent. There is still one C owner for the stock engine
initialization function.

The lifecycle coordinator no longer passes stock absolute engine, output
record, or descriptor addresses. Its C-owned `.bss` buffers are 14,816 engine
bytes, four 100-byte records, one extra 100-byte record and a 264-byte
descriptor. The latest strict map places the engine at `0x20032a84`, descriptor
at `0x20036464`, records at `0x2003656c`, and extra record at `0x200366fc`.
The `.bss` end is `0x20036760`, below the `0x20040000` RAM limit. This avoids
collisions with other source-owned state at the stock fixed addresses.

The ignored callback probe
`build/r1-health-init-profile-binding-20261111/probe.c` executes the actual
primitive and checks the native converter, logger, runtime validator, random
seed, and filter call ordering, including failure paths. The ignored ARM
adapter probe under `build/r1-health-engine-memory-20261111/` executes the
actual production adapter object in Unicorn with modeled children. It checks
the firmware ABI arguments, relocated context, seed, callback bindings, time
slice and propagated `-5` status. These are adapter and primitive checks;
they do not replay the complete native engine against stock or establish
physical sensor behavior.

`build/sources-r1-health-engine-memory-20261111/report.json` compiles all
944 application and 82 bootloader units without failures or duplicate strong
symbols. The strict bootloader links with a valid vector. The strict
application receipt `build/r1-link-health-engine-memory-20261111/report.json`
has nine undefined functions, uses 653,880 of 696,320 flash bytes, and has
no flash overflow. This bridge removes the lifecycle engine import from that
list, but the complete application is still unlinked.
