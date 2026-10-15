# R1 ST25DVxxKC board bindings

`stock_bus_bindings.c` converts the six stock IO veneers and the provider
registration root to C while calling the authenticated ST driver directly.
Its callbacks retain the stock behavior: resource acquire/release return zero,
readiness requests a ten-millisecond delay and returns zero, read/write truncate
the device address to eight bits, and GetTick reads raw RTC1 COUNTER at
`0x40011504`. Resource, transport and delay implementations remain explicit
external seams; they are not replaced with success stubs.

The registration root constructs `ST25DVxxKC_IO_t` using named fields, calls
upstream `ST25DVxxKC_RegisterBusIO`, publishes `St25Dvxxkc_Drv`, and clears that
pointer on initialization failure. It preserves the prior active pointer when
bus registration itself fails, as in the recovered control flow. Object and
active-pointer sections expose placement for the future linker layout but are
not yet placed by an application build.

The literal pool's order is Init/DeInit/IsReady/Read/Write/GetTick, whereas the
public struct's fields put Write at +12 and Read at +16. Stock registration
rearranges those two pool positions while constructing the stack IO object.
Compile-time assertions enforce the typed callback offsets. This corrects the
older correlation note's claim that pool and struct orders were identical.
The readiness callee is `nrf_delay_ms` at `0x784F0`, not an RTOS tick delay.

`make -C r1 sensor-candidates` builds five upstream API units plus these R1
bindings. `make -C r1 st25-bus-oracle` requires Python with Unicorn and compares
90 stock/candidate calls for the six veneers. The test links only those veneers
and intercepts the named provider boundaries in emulation. It compares semantic
arguments, return values and raw RTC reads. Test-only call interception supplies
no production provider implementation. Registration compiles but is not covered
by that veneer test. No actual bus operation, resource lifecycle, elapsed delay,
physical device behavior, complete application link or instruction identity is
proven by these results.
