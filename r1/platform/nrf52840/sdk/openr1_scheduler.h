#ifndef OPENR1_SCHEDULER_H
#define OPENR1_SCHEDULER_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_runtime.h"

typedef void (*openr1_startup_fn)(void);

uint32_t openr1_scheduler_initialize(openr1_startup_fn startup);
void openr1_scheduler_start(void);
void openr1_scheduler_complete_credits(r1_peer_role role, uint8_t completed);
void openr1_scheduler_reset_credits(r1_peer_role role);
bool openr1_scheduler_current_stack(uint32_t **start, uint32_t *words);

#endif
