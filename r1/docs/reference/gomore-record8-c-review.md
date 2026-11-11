# R1 native eight-byte record operations in C

Five native entry points now use C: validation at 0x72420, selection at 0x72550, commit at 0x7260c, getter at 0x68f64 and apply adapter at 0x8ed10. They reuse the existing native-context pointer owner; no new RAM state or assembly was added.

Validation accepts signed first halfwords 15 through 60 and second halfwords 0 through 240, with both hour bytes below 24. Other fields remain unrestricted. Selection reads either the cached record at context offset 304 or the pointed-to record at pointer offset 312 plus two bytes. Ordered word reads/writes preserve overlapping views.

Commit rejects invalid records with result one. Valid records are copied to the pointed-to destination, then refreshed in the cache only when context bytes 184 and 180 are both zero; success returns zero. The getter uses context base plus 4400 and fully writes its local record before copying to the output. The apply adapter discards the commit result and returns zero even for rejected records.

Stock/C replay passes 1,557 cases. It covers validation endpoints and negative halfwords, hour limits, mode zero versus any nonzero value, overlapping record/cache/destination views, cache-control flags and actual health-enable/helper/event-adapter call sequences. Eight compiled defects are rejected, including changed word-copy order and incorrect propagation of the inner rejection status.

Checks compare full guarded context, destination/input/output buffers, public returns, provider order and call-time state snapshots, preserved registers, SP and masks. Record functions execute entirely as C; only authorization and log providers are modeled. Private getter locals and caller-clobbered registers are outside the comparison. Mapped contexts and records are required; no null or invalid-pointer recovery is invented.

All 751 R1 units compile without failures or duplicate strong symbols. All 750 prior objects are identical, including the health-enable unit whose declarations now come from the shared record header. Both record imports close, leaving 136 application and 34 bootloader imports. The R1 manifest check passes; the global check currently flags the concurrent G2 resident_rom_thumb_set.S manifest gap.

These tests do not establish context allocation/initialization, asynchronous operation, physical sensor activation or complete firmware linkage. See [machine-readable evidence](gomore-record8-c-review.json) and [REA selector receipt](gomore-record8-c-rea.json).
