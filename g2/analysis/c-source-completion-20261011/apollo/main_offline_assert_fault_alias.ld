/* Selected invalid-input paths use the same nonreturning BASEPRI-mask,
 * invalid-address store, and loop boundary as the compiled scheduler fault. */
SECTIONS {}
PROVIDE(offline_assert = audio_delay_scheduler_assert);
ASSERT(offline_assert == audio_delay_scheduler_assert,
       "offline assertion boundary must share the scheduler fault body");
