# R1 acknowledgement registry in C

Registration, insertion, removal and timeout cleanup now use C. The implementations reuse the existing 640-byte protocol table, sequence counter and mutex providers. No new state owner or stock executable binding was added.

Insertion selects the first inactive 20-byte row, preserves padding, truncates stored key fields and reads kernel ticks after writing the callback and argument. Registration snapshots explicit/global sequence before locking, retries once after timeout cleanup if full, reloads header bytes for retry and writes the optional identifier only on success.

Removal matches full-width arguments against stored byte/halfword fields, clears activity/callback/argument and leaves metadata and padding intact. It does not free the context. Timeout cleanup snapshots ticks before locking, uses unsigned elapsed time with an inclusive 10,000-tick threshold, frees a nonzero argument without invoking the callback, then clears the row. Native logging order and volatile field reloads are retained.

The stock/C harness passes 372 direct and mixed-sequence cases, 956 actual event-send cases and 870 packet-flush-through-send cases. Checks cover full-table retry, first free row, key width, sequence source, null output/header, callback-zero rejection, timeout equality, tick wraparound, padding, call-time table snapshots, ownership and provider mutation. Eight compiled defect controls are rejected by behavioral comparisons.

The normal license-free build compiles 744 units with no failures or duplicate strong symbols. All 743 prior objects retain their hashes. Relocatable composition has 139 application and 34 bootloader imports; only the two registry imports are removed. The R1 manifest check passes.

The new replays model mutex, kernel tick, logging and free boundaries; event/flush integrations also model transport/allocation. They do not establish physical delivery, asynchronous locking correctness or a complete firmware image. REA confirms the insert/write sequence against the pinned stock bytes. See [machine-readable evidence](ack-registry-c-review.json) and [REA receipt](ack-registry-c-rea.json).
