# Encryption-completion null guard: bounded offline comparison

Four valid nonempty queue projections agree between original bytes, unchanged SDK5.2 secHciCback source and unchanged registered Cordio source. A fifth empty-queue direct-ABI experiment distinguishes stock's unguarded read from the older guarded branch with assertions disabled. The caller source states that the queue must be nonempty; no reachable controller event, vulnerability or hardware consequence is established.

| Input | Original-byte result | SDK source projection | Registered source projection |
| --- | --- | --- | --- |
| Nonempty AES type0 | Dequeue, dispatch; data unchanged | Equal | Equal |
| Nonempty CMAC type1 | Dequeue, reverse16 bytes, dispatch | Equal | Equal |
| Nonempty CCM type3 | Dequeue, reverse16 bytes, dispatch | Equal | Equal |
| Nonempty AES_REV type4 | Dequeue, reverse16 bytes, dispatch | Equal | Equal |
| Empty queue, direct callback ABI | Read-unmapped fault at PC53628E, address34, size1; no type callback | Static source dereference after disabled assertion; native null case deliberately not run | Compiled projection returns after null dequeue; no type callback |

Source assertions are explicitly compiled as no-ops to compare with the stock branch's absent assertion call/null guard. An assertion-enabled source build has a different failure policy and is not modeled. The SDK null behavior is a static source conclusion, not a native execution result or whole-source equivalence claim. All nonempty cases execute both compiled source projections; the older empty case executes its compiled guarded source. Native callbacks and queue geometry are logical stubs, not target ABI implementations.

## Original-byte and source binding

run.py authenticates the locked main SHA25636c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863 and original extents. Original candidate secHciCback536234..536324, WsfMsgDeq4BF9EC..4BFA00 and WsfQueueDeq538C4A..538C6E execute under Unicorn2.1.4 Thumb/M-class. The callback's encryption case event27 calls dequeue at536288, reads returned+52 at53628E without a null branch, optionally reverses16 bytes, then dispatches through secCb.hciCbackTbl[type] atsecCb+60. Authentic secCb base20072CB8 and queue20072CD8 were independently bound in the prior token receipt. Every other reached address fails unless explicitly mocked.

Source extraction retains the complete unchanged secHciCback function body from both files; function hashes in results.json. Public source is freshly acquired from official Packetcraft GitHub at registered3656312d6b73e2a2c1c8b33ee0385bc199dd97e6, SHA25660e8cfd6e8981d28d1a466f41e0a3885acb4e4ea1432a4a27a8a586a73fa0aab; SDK sec_main.c SHA25646ddb191a9235259561949ea16d6248c3dc4c54e42db0890b58cd9b1cf6e8dfc. Original Apache-2.0 notices remain in both cached files. The header/source field projection and the stock queue layout are kept separate.

## Caller and queue preconditions

Source SecAes allocates a request, assigns event/param/token/type, enqueues it **before** HciLeEncryptCmd. AES_REV/CMAC/CCM requests share the security AES queue. Source HciLeEncryptCmd allocates and sends the HCI command; if its command allocation fails it sends nothing and returns void, so the already-enqueued request is not a proof of a subsequently delivered controller completion. Source secHciCback assumes one outstanding queue entry for each delivered encryption completion and removes it before invoking the type callback.

SDK hci_evt.c maps HCI_OPCODE_LE_ENCRYPT command-complete to event27 and hciCb.secCback, allocates a temporary event message, copies returned status/16 data bytes, calls the selected callback and frees the temporary event. This selected source path does not inspect secCb.aesEncQueue before callback. It requires a parsed command-complete and successful temporary allocation; it does not alone prove correspondence to an outstanding request. No malformed transport packet or live event was supplied in these fixtures.

Source SecInit passes secHciCback to HciSecRegister. Authenticated literal5363F8=536235 (Thumb entry) and original registration instructions5367EA..5367F0 load the HCI global and store that pointer atglobal+12; registration-receipt.json records the literal and callback-slot address. Source hci_main.c's HciSecRegister stores hciCb.secCback. This supports the callback identity; the actual receive dispatcher and HCI command transport are not executed here.

The stale-token handler and hardware-error path can drain the queue, but this work does not establish whether an encryption completion can subsequently be delivered for a drained request. Answering that requires controller command acceptance/completion, transport dispatch, event ordering and cancellation/reset behavior. Implementation owns the hardware-error fixtures. Therefore the empty test remains explicitly **direct ABI, outside the asserted invariant**; it must not be promoted to hardware reachability.

## Mocks and preservation

Original queue-dequeue critical-section enter/exit52B8A4/52B8B6 are mocked and checked as one balanced pair per case. WStrReverse56D8F0 is mocked with an exact16-byte reversal and argument checks; actual type callbacks are mocked at distinct per-type addresses with exact buffer/event/handlerId arguments. They do not perform encryption, message forwarding, allocation/free, scheduler or interrupt actions. Event status is0; controller error-status policy is outside the matrix. Type2/DH is not presented as an admissible AES-queue entry.

Stock nonempty writes are restricted to queue/stack; the explicit reverse mock changes only event data+5..+20. Node bytes remain unchanged, queue becomes empty, header/tail event bytes remain unchanged, and return SP/r4-r7 are preserved. The null case stops on unmapped memory34 after a null dequeue with queue empty and before dispatch; it does not claim return ABI preservation. results.json retains all observed reads/writes, arguments and fault details. No firmware low-page mapping was invented to make the null read pass.

Replay is run.py with local clang and installed Unicorn path. One permitted local execution passed the five cases. Outputs are isolated in this directory; no shared projects, canonical ledgers, production bytes/source, index, pins, device state or another track's outputs changed. This closes the finite null-guard semantic comparison. Full queue/event reachability, valid-caller execution and provider/source byte identity remain separate, unresolved obligations.
