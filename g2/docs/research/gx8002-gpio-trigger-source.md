# GPIO trigger configuration recovery notes

Stock entry package0xf540/runtime0x10205fb4, envelope192bytes ending0xf600.
It rejects unsigned port>=32 with -1. For valid ports it calls the recovered
direction setter with INPUT(0), then stores port/callback/private at
0x20027930+12*port in that order. It selects a trigger register, ORs the pin
bit into it where supported, requests IRQ1 with handler0x10205ee0 and null
private argument, and returns0. IRQ request target is0x1002553c.

The switch table at runtime0x1020aca4/package0x14230 has eight targets for
trigger-1. Authenticated analysis script records their mapping:
1 -> GPIO+0x2c,2 -> +0x28,3 -> +0x24,4 -> +0x14,8 -> +0x18.
5/6/7 and values outside1..8 skip trigger MMIO but still install the record
and request IRQ. Do not replace this behavior with an unsupported-value error.

Next reconstruct C and qualify decoded code, including switch dispatch,
port rejection, helper clobbers, live record/volatile MMIO order and20-byte
frame. The ISR presently has a void-argument C prototype; reconcile its IRQ
callback declaration consistently before using it in source, after the active
integration build completes. The table analysis emits no firmware bytes and
does not admit copied stock jump-table data as reconstructed source.

Added model_gx8002_gpio_trigger.py as an independent boundary model. Three
focused tests pass for invalid-port no-effects, unsupported-trigger callback
registration and pin31 register masks. The model records direction and IRQ
request calls but does not execute either helper. Full target interpretation,
helper clobbers/mutations and C compilation remain outstanding.

C candidate now builds natively on macOS:176bytes in192-byte envelope,
SHA d297ea3341d8fef9496991b17e0644d3101b917ba29c18a1bda394c87721b2a4.
It uses the authenticated GPIO enum/callback header and explicit volatile
transactions. -fno-jump-tables generates branches from C; the original
32-byte table is not linked into this candidate. Its retained stock table
region is not yet reclassified or removed from the hybrid.

GPIOISR now takes(int irq,void *data), ignores both, and matches the IRQ
request callback type without casts. Its compiled68-byte payload is unchanged;
864 decoded cases and all13 ISR/model/trigger-model tests pass. The ISR review
report was refreshed for its new source hash. Trigger target qualification
is still pending; this176-byte candidate is not registered or admitted.

Decoded qualification now passes2,520 cases:all valid pins plus32 and high
unsigned boundaries,12 trigger patterns,three seeds and null/non-null callback.
Stock interpreter follows authenticated switch-table targets; compiled C uses
its generated branches. Both compare ordered record/MMIO writes, direction
and IRQ calls, caller clobbers and20-byte frame against the independent model.
Six target tests plus three model tests pass. The routine is registered for
integration. Helper bodies remain modeled and full hardware behavior remains
unqualified. The original unused table has not been claimed as source-owned.

Integration completed with622 passing tests. Full macOS apple-clang build
and verify-artifacts succeed. Codec SHA
585343154388afe22372388a6513227a1a398014b77595549464dec1628e68d0;
package SHAa2e676069c7fac0bd0dd00f2600f0687fc8280f9392f4075bd338fef08ae13df.
The handler's compatible IRQ prototype is included with unchanged handler
instructions. This remains a hybrid with no hardware qualification.
