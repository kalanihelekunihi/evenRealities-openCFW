#include <stdint.h>

extern uint32_t r1_native_health_module_initialize(void);
extern uint32_t r1_native_health_detection_stream_initialize(void);
extern uint32_t r1_native_health_handlers_register(void);
#include "native_health_lifecycle.h"
extern uint32_t r1_native_health_events_register_a(void);
extern uint32_t r1_native_health_events_register_b(void);
extern uint32_t r1_native_health_mode_topics_register(void);
extern uint32_t r1_native_health_activity_enable(void);
extern uint32_t r1_native_health_default_mode_initialize(void);

__attribute__((section(".text.r1_health_startup_nop"))) void r1_health_startup_nop(void) {}

/* Stock calls every stage regardless of earlier raw result words. */
__attribute__((section(".text.r1_native_health_initialize"))) uint32_t
r1_native_health_initialize(void)
{
    (void)r1_native_health_module_initialize();
    (void)r1_native_health_detection_stream_initialize();
    (void)r1_native_health_handlers_register();
    (void)r1_native_gomore_lifecycle_initialize(0);
    (void)r1_native_health_events_register_a();
    (void)r1_native_health_events_register_b();
    (void)r1_native_health_mode_topics_register();
    r1_health_startup_nop();
    (void)r1_native_health_activity_enable();
    return r1_native_health_default_mode_initialize();
}
