/* Authenticated stock callback/message layout, offline only. */
#ifndef OPENCFW_WATCHDOG_CALLBACK_H
#define OPENCFW_WATCHDOG_CALLBACK_H
#include <stdint.h>
typedef struct {uint32_t type,mode,value;} audio_watchdog_message;
void audio_watchdog_tick(void *unused);
void audio_watchdog_emit_type0(uint32_t value);
/* Precondition: stock logging-mask getter returns0 at every call.
 * Logger-enabled branches are deliberately not reconstructed here. */
void audio_watchdog_type6_log_disabled(const audio_watchdog_message *unused);
#endif
