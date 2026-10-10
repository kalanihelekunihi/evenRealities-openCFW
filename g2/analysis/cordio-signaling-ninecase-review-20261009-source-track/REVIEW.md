# Independent review: Cordio nine-fixture result

**Accepted within the reported finite semantic scope.** Independent replay reproduced all nine stock/SDK projections, and old public r20.05c differed in exactly the four short-length fixtures. No canonical admission, whole-SDK revision or vulnerability claim follows.

## Independently checked evidence

- Recomputed the complete 376-byte original extent from the authenticated stock package; it equals the retained original hex and SHA-256 `c26ae1510d3d56ca5de518313cd89389c877a3f1047c4512ab0a547e05db9f7d`. Reviewed the complete instruction listing, including logging branches and common epilogue. Entry UXTH/compare-4/early return precedes the connection lookup. No truncation, opcode replacement or masked comparison was used.
- Reviewed extracted complete SDK/public function bodies and harness construction. The tested SDK function body is verbatim supplied source. The macro has equivalent simple `if(len<4)return` semantics for these side-effect-free arguments. Connection-ID width and role/none constants are checked against authenticated SDK headers in `INDEPENDENT-CHECKS.json`.
- Reviewed the 32-bit stock callback slot offsets and Thumb mock pointers separately from the host C struct. Host fields are mapped by name, not claimed as an Arm struct layout. Stock zero-extends length and handle, and connection/role to byte widths, matching the supplied types. Fixture callbacks retain exact pointer and argument observations.
- Replayed in a new isolated directory using the existing compiler/Unicorn runtime. Added read/write hooks without changing source bodies, dependency values, cases or comparison projection. All nine cases retained packet/control bytes and R4–R7/SP. Observed stock writes were exclusively the saved-register stack; packet reads and writes were zero. Short-length cases observed only stack reads/writes and no dependency/trace query calls. Other observed reads were within authenticated mapped image, control block or stack.
- No unexpected callee was admitted: execution outside the selected function, explicit dependency hooks or stop sentinel fails. Trace-disable query visits and fallback logger remain raw recorded events, distinct from the normalized role-bearing trace event.

## Projection and fixture boundaries

Source compilation is a complete-function projection with supplied dependencies, not a whole Cordio module build. Recording connection/role/callback mocks do not validate real connection tables or downstream parser implementations. Packet pointer 0x20090000 is never dereferenced by this selected function under the nine fixtures; the 32-byte initialized buffer is therefore adequate even for the synthetic direct length-65535 case. It would not be adequate to execute a parser consuming a 65535-byte payload, which was not done.

Trace comparison is deliberately semantic: one role-bearing fallback event corresponds to the source macro, while stock's six platform queries remain separately recorded. Other trace-enable/filter configurations and format providers were not exercised. This distinction is accurate and prevents claiming raw call-trace equality.

The authenticated caller passes L2CAP payload length and the original HCI ACL packet base, then frees it after callback return. The nine direct calls do not execute that caller or deallocation. Its 32-bit length equality admits at most 65531 payload bytes; length 65535 is direct unsigned-ABI evidence only. Framing can statically admit lengths 0..3, but actual transport allocation/reassembly, live connection/callback state and downstream stock behavior remain unproved. No reachable-vulnerability assertion is justified.

## Exact lineage inference

The selected stock function has the **guard-bearing, pre-connection-lookup `len < 4` behavior** represented by the authenticated SDK 5.2 source, unlike the tested public r20.05c body. The tested role/connection/callback dispatch projections agree for the other five fixtures. This identifies a local behavioral source variant; it does not identify the producing private Cordio revision, prove compiled source byte equality, or establish all SDK security changes in stock. A private backport or another guard-bearing revision remains possible.

Deliverables: independent `ninecase-results.json`, `stock-receipts.json`, `INDEPENDENT-CHECKS.json`, instrumented replay `run.py`, generated source harnesses and retained licensed public comparator. The original implementation packet was read only; all new outputs are in this review directory. Root index stayed unchanged during replay. No device, live BLE, production, commit or push action occurred. Further identical fixtures are unnecessary without new evidence.
