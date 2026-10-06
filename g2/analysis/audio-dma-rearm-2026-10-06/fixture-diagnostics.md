# Fixtures and validation limits

The first 879-scenario result and first-verifier.py are preserved. The 894-scenario context result adds explicit synthetic IPSR and repeated IRQ-to-getter cases. A byte-union check found four unexercised TX-ping branch bytes at0x59096c..0x590970; five added edge cases close those bytes in comparison-observable.json (899 scenarios). No source mismatch or executable-source fix was needed. Historical comparisons' verifier manifests are not the current final manifest.

Original IRQ paths reaching0x53c6b2 stop before the notifier body and retain the live frame. Sourceprefix returns captured status, and the verifier records the prospective boundary from bit 4. Neither is an executed queue or full ISR-return proof. Null/unmapped handles, invalid initialized IRQ state, RAM dispatch/queue delivery and arbitrary DMA/NVIC scheduling are outside valid mapped fixtures. Raw register modeling does not enforce hardware read-only/reserved bits or model DMA beats.

INTCLR-side effects, IPSR 60/0 context and clearing next-enable between calls are explicit synthetic fixtures. Noncleared repeated calls cover busy9, including notification despite busy. Prior handoff checked policies stay separate from stock. Prior huge raw-cache positive lengths remain admitted diagnostics limited by instruction budget; no completed-length or cache-physics claim is added.
