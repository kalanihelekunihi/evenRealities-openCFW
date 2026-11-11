# GPIOTE channel and PORT interrupt C source routes

Stock IRQ `0x2d3b4` and PORT helper `0x80ea8` now route to the already compiled,
unchanged pinned Nordic SDK `nrfx_gpiote.c`. Its vector symbol is
`GPIOTE_IRQHandler`; its C `port_event_handle` is inlined into that symbol by the
normal compiler. The PORT row records a tested source relationship, not an
independent object symbol or exact body selection. No second implementation,
firmware state owner, source unit, compiler flag, or manifest change is introduced.

REA covers the 156-byte IRQ body, 202-byte PORT body, and latch collection helper.
The locked application vector at index 22 contains `0x2d3b5`. Assertions compiled
against the actual SDK type confirm a 128-byte control block: handlers at +0,
48 pin assignments at +64, eight PORT encodings at +112, configured-pin bits at
+120, and driver state at +126. The fixture binds the actual compiled static
`m_cb` at native `0x2002c168`. This controlled placement is not proof of a final
firmware linker binding.

The handler collects and clears all enabled channel events before dispatching any
channel callback. Pending IN events require the register value one and the
corresponding interrupt mask; disabled events remain pending. PORT is collected
when its event register is one, independently of its interrupt-enable bit. Both
GPIO latch registers are read and cleared before channel callbacks. Channel
callbacks then read the current pin, polarity and handler for each captured
channel. PORT processing uses the captured latches, flips pin sense, clears that
pin's latch, applies the configured polarity filter, reloads the assigned handler,
and repeats when new latch bits are observed.

68,797 paired sequences deliver two IRQs apiece (137,594 paired invocations):

- 65,536 cover every eight-channel pending/enabled mask combination.
- 144 cover selected null-handler masks and non-one raw event register values.
- 3,072 PORT cases cover all eight slots, pins 0/31/32/47, polarity 0/1/2/3,
  sense disabled/high/low, latch presence, null/non-null handlers and PORT masks.
- 45 combined cases change later channel configuration/handler, re-pend a channel,
  disable interrupt masks, re-latch a PORT pin for another pass, or change a PORT
  handler during a channel callback.

Ordered MMIO reads/writes, callback pin/polarity and control-block snapshots,
final driver/register memory, return callee registers, SP, masks, and adjacent
state guards match. Six negative controls reject ignored interrupt enables,
missing event clear, lost earlier channels, wrong callback pin, missing sense
inversion and an incorrect PORT polarity gate.

Native channel callbacks use a 32-byte frame and PORT callbacks a 72-byte frame;
the compiled C IRQ uses 48 bytes for both. Private frames and live callback callee
registers are not treated as equal. GPIO LATCH write-one-to-clear is modeled with
post-store effects; autonomous DETECT re-latching, pin levels, electrical behavior,
real exceptions, invalid assignments, arbitrary aliases/faults and concurrency
remain unproven. Callbacks are modeled boundaries. CONFIG fields and pending
registers are controlled fixture inputs, not a claim of physical event generation.

Qualification compiles the SDK unit but selects no exact regions. All 589 source
and object hashes plus the manifest were revalidated against the prior successful
normal R1 report, with 164 application / 34 bootloader imports and no compile
failures or duplicate strong symbols. Firmware source is unchanged; no new build
was needed for these source-route updates. The existing canonical hybrid artifact
and source-plan hash were revalidated: 4,245 source-built, 641,915 executable
fallback and 248 resource bytes. Source-built includes admitted assembly/data.
The locked application SHA is retained; complete source-only rebuilding and
byte-identical C reconstruction remain unproven.

Machine-readable evidence: `gpiote-irq-c-review.json`. Reproducible ignored probes:
`build/goal-r1-gpiote-irq-c/`.

A subsequent [bounded observer replay](irq-observer-review.md) passes the full
original matrix with MMIO hooks restricted to their register ranges.
