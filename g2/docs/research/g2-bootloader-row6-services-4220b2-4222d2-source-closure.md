# G2 bootloader row-six services and dispatcher source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Three authenticated executable bodies at `[0x004220B2,0x004222D2)` now
compile from maintained clean-room C at their exact stock addresses. Apple
clang 21 and Homebrew clang 22.1.8 reproduce all 508 executable bytes exactly;
the two intervening 18-byte literal seams remain separately authenticated
official data rather than being mislabeled as source code.

The row-six enable transaction maintains client membership, coordinates both
selector modes using client `0x35`, creates/configures/starts the retained
service handle on the first client, releases the unused mode, finalizes the
successful handle and performs ordered bitmap/handle/mode rollback on failure.
The disable transaction is idempotent and stops/destroys the retained handle,
clears pending state and releases the selected mode only for the last client.
The dispatcher narrows its kind to one byte, forwards kinds `4`, `5` and `6`
to the maintained mode, dual-mode and bitmap-client services, and maps every
other kind to status `7`.

`runtime_row6_services_4220b2.c` is 13,243 bytes with SHA-256
`1aff00645c2f9ca84371f0e0a7ef12eb819e3fc1aa499d1d52afacce433080af`.
The installed 348-byte enable body has SHA-256
`701cc62514c5618aece1f206044e7815375082c6e4a9afa4eafd0e331f331e96`
and unrelocated SHA-256
`fc033ae92b93933dc5893c860c1eb07661db5487e374bf9860f7fa8a88a44679`.
The installed 110-byte disable body has SHA-256
`f26f053665f5477df6aa97d2e596f08b7045112332919102a5b1dd72d219ea36`
and unrelocated SHA-256
`d2e1cf083225fef4b2027e8a0dc495d1e360df64e65ccb083191f98b775827f1`.
The installed 50-byte dispatcher has SHA-256
`7da05bfcd4b489183db4a2a1becfbe3bb7a0e3dc297e74e632c00e454d653164`
and unrelocated SHA-256
`7ddb87ecef016bd9ed161aa44bfee69d7f8feba13a61f77bc27f9001d741882b`.
The literal seams have SHA-256 `34fb2e40…99a9e` and `08388290…a151a`.
Thirty-one strict calls bind maintained bitmap, critical, selector-mode and
mode-family services plus retained handle lifecycle providers. Seven focused
tests pin bodies, seams and successor; exercise first/existing clients,
readiness and start rollback, absent/nonfinal/final disable and dispatcher
routing; and compile both reviewed profiles.

Canonical accounting becomes 18,971 source-owned, 16,528 generated patch, 16
alignment, and 128,325 retained official bytes, including 362 cave bytes and
3,384 exact in-place bytes across 232 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,594,698-byte flash plan has SHA-256
`462379978f2f8ef4a6299a88ea98370be2911f3fbfd0a0606af9c24551e0117f`
with 6,602 placed, two unresolved, five container-only and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but live interrupt timing, retained handle-provider behavior, shared
bitmap/state ownership, selector-mode coordination and physical row-six
effects require authorized hardware evidence. That evidence is unavailable
because no authorized responsive right temple exists and the left temple must
remain stock. Firmware-wide functional completeness is not claimed; after the
authenticated padding/literal seam, the next executable body begins at
`0x004222F0`.
