# Native named interrupt GPIO records

The seven 44-byte descriptors at stock `0x200070C0` are source-owned typed
records, including `nfc_gpo_irq` on P0.03 and the two P1.01 descriptors with
different names. Their embedded registry records begin at +16; the callback
word is +40. Configuration bytes and initial zeros come from authenticated
stock scatter execution (`gpio/stock-initialization.json`).

Six recovered native bodies compile: event-open (`0x54B90`), IRQ dispatch
(`0x6ED94`), register-all (`0x54C24`), callback
set/clear (`0x54AFC`), pin read (`0x54ED0`), and close (`0x54B40`). Lookup uses
stock's name comparison rather than requiring pointer identity. Callback
storage accepts zero. Read stores one byte from the compiled Nordic GPIO HAL.
Close disables and uninitializes an opened pin before clearing its flag.

```
make -C r1 named-gpio-candidate
make -C r1 named-gpio-oracle PYTHON=/tmp/r1-source-venv/bin/python
```

All 308 initial record bytes match stock after name relocation, and 202 bounded
comparisons pass. The test uses the actual registry and GPIO read body. It
intercepts nrfx disable/uninit to verify their API ordering and arguments;
it does not test those SDK internals. Open/close SDK calls are intercepted at the final nrfx seams to check their
configuration, return-status handling and order. Those SDK bodies remain explicit
production link dependencies. Newlib strcmp is a binary test dependency. Real interrupts,
electrical effects, physical timing and full application startup remain open.

Only four of the six tested stock entries are separate ownership-ledger rows;
the frontier count preserves that existing scope.

Open preserves the original input-disconnected PIN_CNF write, initializes nrfx
only when needed, copies the four-byte config template with recovered sense
and pull, installs the real source IRQ dispatcher, and enables events. Stock
ignores init/in-init errors and marks opened; the C body preserves that behavior.
IRQ dispatch walks every record and calls all matching nonzero callbacks in
record order, including both P1.01 descriptors. Ghidra-MCP's readback of the
52-byte original dispatcher independently matches the locked image bytes (the
MCP and other Ghidra adapters share a backend, not independent semantics).
All consumed Nordic headers are authenticated against the pinned SDK archive.

The component now relocatably links against the actual compiled nrfx GPIOTE
object and native registry/TWI objects (`gpio/integration-report.json`). Six
private-type assertions prove the recovered 128-byte control-block layout and
eight low-power slots. This resolves the six nrfx entry-point requirements in
the component link. Remaining symbols are C runtime memory/string functions
and the separate ST25 millisecond-delay seam. The differential oracle still
intercepts final nrfx calls; linking the real object does not establish its
runtime behavior or a complete application image.

`verify_gpio_sdk_execution.py` additionally executes the actual source-linked
nrfx init, input init, enable, disable and uninit bodies without provider
interception. Its 29-call differential against original Thumb matches statuses,
61 candidate peripheral/core writes and the relocated control state. Seven
opens (including the shared-pin duplicate), repeated-open shortcuts and six
unique-pin closes are exercised. Newlib strcmp/memset remain attributed binary
test dependencies. Duplicate-close coherence and asynchronous IRQ delivery are
still gates. This supersedes the earlier link-only runtime limitation for these
bounded lifecycle paths, not for all driver behavior.
