# R1 RTT-only default logger initialization

`native_log_default_backends.c` compiles the unmodified pinned SDK initializer
with `NRF_LOG_BACKEND_UART_ENABLED=0`, scoped locally after loading the shared
candidate configuration. Stock entry `0x7968c` initializes RTT, registers its
backend at debug severity 4 and enables its control byte. It has no UART path.
The generated SDK example defaults previously enabled UART in this unit,
introducing two imports without corresponding stock calls in this function.

The wrapper replaces the SDK source entry in the manifest; it does not add a
second initializer. Other compilation units retain their existing configuration.
The RTT backend's 16-byte metadata and name match stock at test bindings, with
an eight-byte control block. Executing the stock RW initialization decoder
confirms control bytes `00000000ff000000` at `0x200079bc`. REA/Ghidra read the
native initializer, backend pointer and metadata.

The production object passed 376 stock/C scenarios comprising 1,128 paired
initializations. Tests check RTT initialization before registration, backend
pointer and severity, provider changes to control bytes, repeated calls, full
registration return values and both PRIMASK settings. The enable byte becomes
one while the remaining control bytes retain the registration provider's values.
Callee restoration, SP and interrupt masks are checked; both provider frames
are eight bytes. Four negative controls reject UART inventory, skipped RTT
initialization, skipped enable and incorrect severity. The UART control is
rejected by linked backend inventory; the others fail runtime comparisons.

RTT initialization and logger registration are modeled providers. No real
debugger transport, log delivery, private spills, nonargument caller-clobbered
registers, live provider registers or APSR equality is proven. Read-only metadata
uses fixed test bindings; arbitrary metadata mutation and faults are excluded.
Test address placement does not establish final linking.

All 590 R1 units compile and compose without known failures or duplicate strong
symbols. The other 589 objects are unchanged. Application imports decrease from
162 to 160; bootloader imports remain 34. The pinned SDK source is unchanged,
and no UART symbols remain in this wrapper object.

Exact qualification selected no new regions. The source plan and hybrid
application remain unchanged, with locked SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and 4,245 source-built, 641,915 binary-pull-through and 248 resource bytes.
A complete source link, complete hardware support and a byte-identical source
rebuild remain unproven.

The [receipt](rtt-default-c-review.json) records sources, compiler arguments,
hashes and evidence. Ignored reproduction inputs are under
`build/goal-r1-rtt-default-c/`; current reports are
`build/sources-goal-r1-rtt-default-c/report.json` and
`build/hybrid-goal-r1-rtt-default-c/build-report.json`.
