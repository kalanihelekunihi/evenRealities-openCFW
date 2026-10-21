#pragma once
#include <stdint.h>
uint32_t clock_reset_should_enter(void);
uint32_t clock_reset_has_requests(void);
void clock_reset_reinitialize_retained(void);
void clock_reset_gated_path(void); /* partial path, precondition required */
