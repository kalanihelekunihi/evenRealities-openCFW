# R1 Goodix I2C transport reconstructed in C

Five native board functions now compile and participate in the normal R1
application composition from `r1/src/application/goodix/stock_i2c_transport.c`.
These bodies contain no inline assembly. The source plan is unchanged; these
are behavioral candidates without instruction identity or final integration.

REA on the locked stock image confirms that demo initialization at `0x2d87c`
registers device ID zero with write callback `0x6f90f` and read callback
`0x6f8fb` through registration at `0x2aaf8`. This corrects the interpretation
of the historical frontier label `r1_sensor_reg_write16`: its entry `0x6f8fa`
is the five-argument read callback. Historical source labels remain in the
frontier; candidate symbols describe the observed contracts.

| Entry | C candidate | Native behavior |
| --- | --- | --- |
| `0x509b0` | `r1_goodix_i2c_open` | Load cached device; dispatch slot 08 |
| `0x509bc` | `r1_goodix_i2c_write_request` | Fill write request; dispatch slot 14 |
| `0x5084c` | `r1_goodix_i2c_read_request` | Fill read request; dispatch slot 10 |
| `0x6f90e` | `r1_goodix_i2c_write` | Write request with code zero; return one |
| `0x6f8fa` | `r1_goodix_i2c_read` | Swap command halfword; read request; return one |

The cached device is at `0x200076cc`; the shared 20-byte request starts at
`0x200076dc`. The bus handle uses the existing `r1_ppg_bus_device` owner from
`native_peripheral_bindings.c`, populated by `r1_ppg_device_bind`; the initial
separate `r1_goodix_i2c_device` owner was removed after tracing that initializer.
See [the binding integration review](goodix-cache-c-integration-review.md).
Fields are address byte +0, command halfword +2, write buffer
word +4, write length halfword +8, read buffer word +12 and read length
halfword +16. C storage uses dedicated sections requiring those placements
in a final source linker. Device initialization follows the existing registry
binding rather than an inferred default handle.
The [cold-state correction](goodix-cold-state-review.md) supplies the stock
request initializer: address `0x24` and both lengths one, with other fields zero.

Native write order is command, address, conditional write-buffer update,
write length. A null write buffer retains its previous value. Read order is
command, address, read length, read buffer. Both paths load the cached device
after updating the request. Volatile fields preserve those access widths and
orders. The read callback ignores command length and unconditionally loads
one halfword; no new guard or fallback was added. Both callbacks discard the
transport status and return one, as stock does.

The ignored probe `build/goal-r1-goodix-hardware-binding/verify.py` passed
630 stock-versus-C cases (1,260 executions). It executes the actual stock and
reconstructed registry dispatchers, models their final operation callbacks,
and compares shared-state memory accesses, command loads, dispatch arguments,
request contents, preserved registers, stack restoration and interrupt masks.
Cases cover null devices, missing operations, operation errors, null buffers,
retained request fields, and full-width values truncated by native stores.
Private stack bytes and void return register residue are outside this check.

`make sources-check` passes. The full R1 build at
`build/sources-goal-r1-goodix-cache-final/report.json` compiles 563 units without
failures or duplicate strong symbols; imports remain 210 application and
34 bootloader. The 19 build-tool tests pass. Evidence hashes and REA snapshot
location are recorded in [the machine review](goodix-i2c-c-transport-review.json).

Physical I2C behavior, concurrency, invalid-pointer cases beyond the modeled
inputs, electrical initialization of the hardware device, final source placement,
and byte equality remain unproven. The upstream `gh3026_*` demo hooks remain
unbound: their empty, unconditional SDK macros are not an established R1
integration point. These native functions provide a checked transport boundary
for that further work without adding success-only demo stubs.
