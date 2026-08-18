#ifndef OPENR1_GOMORE_ZEPHYR_H
#define OPENR1_GOMORE_ZEPHYR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_runtime.h"

/* Reconcile the source-built engine and execute the complete reconstructed
 * topic-input, resampling, sixteen-stage, and output-snapshot path. */
int openr1_gomore_zephyr_sync(r1_runtime *runtime);
int openr1_gomore_zephyr_poll(r1_runtime *runtime);
/* Recovered time/profile/failure reset: discard resume state, disable the
 * dynamic sleep-optical slot, clear staged input, and initialize afresh. */
int openr1_gomore_zephyr_reinitialize(r1_runtime *runtime);
bool openr1_gomore_zephyr_initialized(void);
int32_t openr1_gomore_zephyr_last_status(void);
size_t openr1_gomore_zephyr_allocated_bytes(void);
bool openr1_gomore_zephyr_previous_state_available(void);
bool openr1_gomore_zephyr_previous_state_restored(void);
uint32_t openr1_gomore_zephyr_previous_state_writes(void);
uint32_t openr1_gomore_zephyr_previous_state_write_failures(void);
uint32_t openr1_gomore_zephyr_updates(void);
uint32_t openr1_gomore_zephyr_update_failures(void);
uint32_t openr1_gomore_zephyr_activity_publication_failures(void);
uint32_t openr1_gomore_zephyr_sleep_publications(void);
uint32_t openr1_gomore_zephyr_sleep_publication_failures(void);
uint32_t openr1_gomore_zephyr_authorization_failures(void);
uint32_t openr1_gomore_zephyr_reinitializations(void);
uint32_t openr1_gomore_zephyr_reinitialization_failures(void);

#endif
