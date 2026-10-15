/* Apollo ring-connect mutex wrappers 0x5e438e and 0x5e43be. */
#include <stdint.h>

extern uint32_t audio_registry_ring_connect_mutex_handle; /* native 0x20074a84 */
extern uint32_t audio_registry_ring_connect_mutex_init_5e4326(void);
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* selected 0x4497b6 */
extern int32_t audio_file_mutex_release(void *);        /* selected 0x44981c */

uint32_t audio_registry_ring_connect_enter_5e438e(uint32_t unused) {
    (void)unused;
    if(audio_registry_ring_connect_mutex_handle==0u &&
       audio_registry_ring_connect_mutex_init_5e4326()!=0u) return 0u;
    return (uint32_t)(audio_file_mutex_acquire(
        (void *)(uintptr_t)audio_registry_ring_connect_mutex_handle,UINT32_MAX)==0);
}

void audio_registry_ring_connect_leave_5e43be(void) {
    if(audio_registry_ring_connect_mutex_handle!=0u)
        (void)audio_file_mutex_release(
            (void *)(uintptr_t)audio_registry_ring_connect_mutex_handle);
}
