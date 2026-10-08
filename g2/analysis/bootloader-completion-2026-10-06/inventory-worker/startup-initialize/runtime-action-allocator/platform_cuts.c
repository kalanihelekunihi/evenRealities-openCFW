#include <stdint.h>

volatile uint32_t test_suspend_calls;
volatile uint32_t test_resume_calls;
volatile uint32_t test_malloc_failed_calls;
volatile uint32_t test_mask_calls;
volatile uint32_t test_event_count;
volatile uint32_t test_events[128];

static void event(uint32_t value) { test_events[test_event_count++] = value; }
void opencfw_bl_scheduler_suspend(void) { test_suspend_calls++; event(1); }
uint32_t opencfw_bl_scheduler_resume(void) { test_resume_calls++; event(2); return 0; }
void opencfw_bl_malloc_failed(void) { test_malloc_failed_calls++; event(3); }
uint32_t opencfw_bl_mask_interrupts(void) { test_mask_calls++; event(4); return 0; }
