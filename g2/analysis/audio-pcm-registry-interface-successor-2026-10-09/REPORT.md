# Corrected PCM registry interfaces

Stock disassembly and the preserved registration table resolve a semantic error in the predecessor's offline symbol names. **Five dispatcher mechanics were already recovered**; this successor gives them correct identities and adds **four newly exercised wrapper bodies**: true tempco-suspend0x4803DC, LP-auto initialize0x4803F2, enable0x480408, disable0x48041E. TON update remains the predecessor body. The source contains eight no-argument wrappers, four repeated and four new; do not count eight new functions.

| Wrapper | Registry slot | Meaning |
|---|---|---|
|480358|20073284|Before override|
|48036E|20073288|Before enable|
|480384|2007328C|After enable|
|4803AC|20073290|TON initialize|
|4803DC|20073298|Tempco suspend|
|4803F2|200732A0|LP-auto initialize|
|480408|200732A4|LP-auto enable|
|48041E|200732A8|LP-auto disable|

Each reads its volatile slot twice if non-null, calls the selected function and forwards return; null returns zero. **64 original-instruction comparisons PASS** against the exact receipt-bound ELF, source-guarded throughout reached native paths. Before/after enable, TON init and all LP-auto known children execute actual recovered source. The suspend and before-override tests cover null only, not nonnull child behavior. Synthetic registration is deliberately distinguished from actual stock installation.

The sealed registration batch's168 family comparisons assign no slot index10 (tempco suspend), while public SDK assigns it under NO_TEMPSENSE_IN_DEEPSLEEP. No active stock suspend child is established. Physical power state, runtime registry mutation and exception/scheduling behavior are not proven. The predecessor's file-level PASS limits use misleading names; this report supersedes their semantic interpretation, preserving immutable originals.

[Reusable interfaces](../../components/audio/pcm_registry_offline/registry.h), [source](../../components/audio/pcm_registry_offline/registry.c), [exact receipt](reproduction-receipt.json), [comparisons](results.json). Author-validated offline only; no independent review, full firmware closure or byte equality.
