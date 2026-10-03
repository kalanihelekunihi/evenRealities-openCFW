# Independent review 6541

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes, all ten observation inputs, and the three source words match the pinned image. The word at 0x4341A0 is 8 and is dereferenced in the mapped heap allocation/deallocation/initialization paths as an allocation header size. The word at 0x4341B8 is 12; the allocator initialization path uses it in doubled overhead arithmetic, while the same mapped family compares adjusted sizes against the constants at 0x4341A0 and 0x4341BC. The latter word is 0x40000000 and is used as the upper adjusted-length bound. These are local code-level roles supported by the cited instruction ledgers, not conclusions from the constants' numeric values alone.

All ten recorded consumer observations reconcile with their pinned maps. This does not establish neighboring words as data, full allocator behavior, or platform/hardware meaning. No canonical files or gates changed.
