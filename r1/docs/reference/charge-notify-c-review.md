# Charge-state notification in C

`r1/src/application/runtime/native_charge_notification.c` replaces the symbolic
assembly routine at stock 0x838e0 with ordinary C. The packet owns two initialized
words copied from the existing immutable template. The charge byte is truncated
to eight bits; full charge selects state 3, otherwise active charge selects 1,
and the remaining case selects 2. Full charge retains priority when both
independently sampled predicates are true. Both queries still execute in their
original order. The phone handle is fetched afterward, and the common response
entry receives operation 127, first word 1, sequence 0 and seven payload bytes.

Fresh REA windows cover the notification routine, event adapter, template and
saved-word YHM status entry and match the preserved application. The template
pointer resolves to 0x9a44c; the device-status routine uses a distinct table, so
no data-owner consolidation is inferred from identical contents. Both template
words remain unchanged. No new state owner, source unit or source-plan selection
is added.

The final normal product object passes **2530 stock/previous/new cases (7590
executions)**. The 570 isolated cases check arbitrary full-width getter values,
byte truncation, state priority, invalid handles and send statuses. The 1960
hardware-chain cases execute the actual charge predicates, charger-state
mapping and saved-word YHM status implementation. Modeled ready/read providers
exercise partial/non-writing reads, ignored read errors, changing states between the two queries and every incoming low status byte. Assertions check
that the saved word is retained at each read; the lower driver adapters remain
because that fallback is meaningful. The compiled C notification preserves it
under the recorded compiler/profile; this is not a cross-compiler register-state
claim.

Both groups include actual event-adapter execution: the authenticated-phone
predicate is modeled, while byte truncation and the payload-equals-one gate run
in the adapter. The actual common header function executes on every published
case. Independent oracles check the seven-byte payload and eight-byte header,
provider order, repeated state reads, invalid-handle suppression, saved registers,
SP and interrupt masks. The charge-byte getter, phone handle, authentication,
ready/read and final response services are modeled boundaries. This does not
execute the final encoder or BLE delivery. Private provider frames, raw live
temporaries and incidental void-entry outputs are excluded.

Five compiled defects are detected: wrong state priority, reordered queries,
corrupted tail bytes, wrong operation and wrong payload length. The final normal
implementation is rerun after controls. All **801 units (719 application, 82
bootloader)** compile without failures or duplicate strong symbols. Imports
remain 95 application and 22 bootloader linker metadata symbols. Strict GNU
bootloader linking and R1 manifest checks pass. All 798 other nongenerated prior
object hashes are unchanged; generated boot vectors/crypto retain identical
allocated bytes and relocations. The global check retains the unrelated unlisted
G2 resident-ROM assembly file.

[The receipt](charge-notify-c-review.json) records input, object, REA and probe
hashes. Physical charger sensing, GPIO timing, asynchronous state changes, radio
transport and complete application final linking remain unverified. The lower
register/frame adapters and other firmware assembly are not removed by this
change.
