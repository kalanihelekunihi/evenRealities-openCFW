# SPIM2 completion IRQ C source route

Stock IRQ `0x31a94` now routes to the unchanged, already compiled pinned Nordic
SDK `nrfx_spim.c` symbol `SPIM2_SPIS2_SPI2_IRQHandler`. REA covers its 76-byte
native body and literal bindings. Application vector index 51 contains `0x31a95`.
No firmware C, state owner, source unit, manifest, or compiler flag is changed.

Compiled assertions confirm a single SPIM instance, SPIM2 at index zero, and a
36-byte control block: callback at +0, context at +4, 20-byte event at +8, driver
state at +28, busy at +29, chip-select polarity/pin at +30/+31, MISO/ORC at +32/+33.
The fixture links the actual C object with its static state at native `0x2002c280`.
This controlled placement is not a final firmware linker-binding proof.

On nonzero END, both paths clear and read back the event, deactivate software
chip select when its pin is not 255, clear busy, mark the stored event DONE and
tail-call the callback with event pointer and context. Active-high SS is cleared;
active-low SS is set. GPIO ports zero and one are exercised. END zero leaves the
state and GPIO unchanged and does not call back. Completion is driven by END,
not by the previous busy value. The descriptor and unused bytes are preserved.

2,880 stock/C sequences deliver two IRQs each (5,760 paired invocations). They
cover END 0/1/256/`0xffffffff`, SS pins 0/31/32/47/unused, both polarities and busy
states, three contexts and three initial byte patterns. Callback mutations re-arm
END, busy and SS; change polarity, handler, context and descriptor; or switch to
unused SS. Ordered MMIO, complete callback-visible state, arguments, final driver
and mapped peripheral memory, return callee registers, SP, masks and guards match.
Six negative controls reject inverted SS polarity, using the unused pin, retained
busy, lost context, retained event type and missing END clear.

At every completion callback, incoming SP and R4-R11 are restored and caller LR is
forwarded in both implementations. This tail contract is checked with an ordinary
return target, not real exception return. Internal MMIO frame depths differ:
stock uses 24 bytes plus an eight-byte clear-helper frame; C uses zero or 12 bytes.
APSR and other caller-clobbered registers are excluded. OUTSET/OUTCLR effects are
modeled; real SPI/EasyDMA traffic, SS electrical timing, interrupt delivery,
concurrency, null handlers, corrupt states and arbitrary aliases/faults are unproven.

The adjacent TWIM1 working-frontier span is corrected from 410 to ten code bytes.
REA shows a short stub loading peripheral `0x40004000` and control block
`0x2002c21c`, then branching to `0x939a0`, followed by padding and a literal. Its
old span included unrelated routines. Vectors 19/20 independently point to the
TWIM0/1 stubs. Authenticated inventories are unchanged. This is a boundary-only
correction: TWIM shared-dispatch behavior and its C route remain unvalidated here.

Qualification compiles the SPIM SDK unit and selects no exact regions. All 589
normal source/object hashes and the manifest were revalidated against the prior
successful R1 report, with 164 application / 34 bootloader imports and no compile
failures or duplicate strong symbols. The existing canonical hybrid artifact and
source-plan hash were revalidated: 4,245 source-built, 641,915 executable fallback
and 248 resource bytes. Source-built includes admitted assembly/data. The locked
application SHA is retained; complete source-only rebuilding and byte-identical
C reconstruction remain unproven.

Machine-readable evidence: `spim2-irq-c-review.json`. Reproducible ignored probes:
`build/goal-r1-spim2-irq-c/`.

A subsequent [bounded observer replay](irq-observer-review.md) passes the full
original matrix with MMIO hooks restricted to their register ranges.

The subsequent [TWIM IRQ review](twim-irq-c-review.md) now validates both TWIM
entries, their shared dispatcher and completeness helper.
