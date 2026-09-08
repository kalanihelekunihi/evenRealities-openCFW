# OTP write wrapper candidate

Recovered runtime_gx8002_flash_otp_write.c at package0x15ecc/runtime10023eb8.
Default native macOS-Os gives240/236 bytes. Priority register allocation gives
228 with stock40-byte saved frame(r4-r11,LR,r16); selected for this candidate.
No-shrink-wrap leaves240; combined priority/no-shrink228; disabling loop
invariant movement gives224 but not selected or qualified. No-ivopts240.

Reads selected_device, descriptor and flags&7 before checking zero length,
which returns-1. Wrapped offset+length greater than descriptor size returns-1.
Then reads base, adds offset, reads stride, adds region*stride; signed
manufacturer must equal0x5e/0x85. No descriptor reload occurs across helpers.
Accepted writes wait, enable, set command0=0x42 and encode address. If wrapped
length+(address&255)<=256, transmit with current address_bytes+1 and length.
Otherwise first chunk is256-(address&255); subsequent chunks encode updated
address, wait, enable, reload address_bytes+1, and transmit at most256 bytes.
Transport return values are ignored. The stock return accumulator updates only
when nonzero; source preserves this conditional instead of simplifying it.
Final wait precedes return. Buffer advances use unsigned address arithmetic.

Decoded bounds/overflow, call order, pointer/width mutation, accumulator,
clobber and frame qualification remains. Source fitting alone is not admission;
this candidate is not registered. No hardware write was performed.

Prepared independent expected-event model in model_gx8002_flash_otp_write.py.
It specifies state/descriptor read order, zero/bounds/manufacturer rejection,
page chunk arguments, helper order and address-width reloads. Modeled encoder
and transport change width after calls, exposing cached-width mistakes.
Four model tests pass: zero descriptor reads, bounds short circuit, partial/
full/final pages with wrapped buffer and changing width, and wrapped sums
accepting one near-UINT32_MAX transfer. No decoded stock/source execution has
yet been checked against this model. Model tests alone do not qualify code.

Initial decoded stock/source executor now passes1344 cases against the expected
ordered effects. Cases cover six offsets includingUINT32_MAX, seven lengths,
four manufacturers, four region flag patterns and two helper-clobber seeds.
Both streams must use the40-byte frame, preserve ABI registers, consume all
expected reads/writes/calls and return the expected count/error. Address width
changes are observed after each modeled encoder/transmit call. Synthetic
wrapped payload pointers are not physical buffer validation. Broader capacity,
base/stride/large-length overflow cases and rejection tests remain.

Added ten decoded overflow/clobber cases to the1344-case baseline. These
cover near-UINT32_MAX one-call lengths, wrapped bounds, wrapped base/stride
address arithmetic, multi-page writes crossing address zero and width initialized
toUINT32_MAX so helper mutation wraps it. Both decoded streams match expected
traces/results. Physical validity of synthetic buffers remains unproven;
rejection tests and admission remain.

Six decoded-executor rejection tests pass (bad helper frame/saved set, unknown
helper, missing effect, wrong transmit arguments, unknown opcode), alongside
four model tests. Reviewed admission adapter/report regenerated successfully,
including1344 baseline and ten overflow cases. Registered source and ten tests
for full codec integration; package completion awaits that build and artifact
verification. No hardware OTP operation was performed.

OTP write fully integrated:224 tests pass; native macOS package build and
verify-artifacts pass.116 functions/132 code occurrences/16 data regions;
7700 C,2040 data,80 metadata,314 fill,315958 retained. Codec SHA:
fd31c84f5ac7ccb96f4f4cbf823f4b00ffbff58fea7d403b05608ba64dcb7904.
Package SHA:6da65e662d06b6d2ac448ae968735d917bbe22f5f062a8f12cc0493ec39fb9ca.
Candidate pin is not hardware proof or vendor identity. Full goal active.
