# Queue query APIs resolve CMSIS dependencies

The existing mutex-kernel unit now includes the pinned FreeRTOS `uxQueueSpacesAvailable` and `xQueueGetMutexHolder` bodies. Both use its established native-layout `Queue_t`; static assertions bind messages-waiting, length and mutex-holder offsets to 56, 60 and eight. No duplicate queue type, owner or scheduler state is introduced.

Free-space lookup reads length minus messages waiting inside a critical section. Mutex-holder lookup checks the mutex marker and reads the holder inside the critical section, returning NULL for other queue types. Both return the sampled value after leaving the critical section. Pinned assertion statements and current build assertion policy are retained; invalid handles keep upstream preconditions.

The [receipt](rtos-queue-query-c-review.json) records 336 API checks across empty/full/partial counters, raw-width arithmetic, mutex/non-mutex records, holder values and controlled metadata changes at critical entry/exit. Return snapshots, critical-call order, final queue bytes, balanced stack, saved registers and masks agree with the independent field/ordering oracle. Four defects with reversed subtraction, wrong holder field or missing critical entry/exit are rejected.

These are pinned upstream compatibility providers, not stock query-function identity claims. Critical callbacks are modeled. Full scheduler operation, invalid-object fault behavior, physical devices and a complete firmware image remain unverified.

The normal report is `build/sources-goal-r1-rtos-queue-query-final/report.json`: all 729 units compile without failures or duplicate strong symbols. Application imports fall from 172 to 170, resolving the two CMSIS references; bootloader imports remain 34. Only the mutex-kernel object changed; 728 objects remain unchanged. All 28 pre-existing instruction sections and named relocations are unchanged. The prior source bytes, including mixed line endings, are preserved as an exact prefix; only the new APIs and offset assertion are appended. Both manifests pass `make sources-check`; no source-plan selection was added.
