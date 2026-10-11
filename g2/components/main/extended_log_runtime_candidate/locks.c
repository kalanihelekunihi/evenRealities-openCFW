/* Stock Main 0x44aa98/0x44aaa0 wrappers through 0x44aa40/0x44aa56.
 * Mutex cell 0x20074578 is authenticated by literal at 0x44aafc. */
#include <stdint.h>
extern int32_t audio_mutex_acquire(uint32_t tagged_mutex,uint32_t wait_ticks);
extern int32_t audio_mutex_release(uint32_t tagged_mutex);
static volatile uint32_t *const logger_mutex = (volatile uint32_t *)(uintptr_t)0x20074578u;
void g2_log_lock_enter(void) {
    if (*logger_mutex != 0u) (void)audio_mutex_acquire(*logger_mutex,1000u);
}
void g2_log_lock_exit(void) {
    if (*logger_mutex != 0u) (void)audio_mutex_release(*logger_mutex);
}
