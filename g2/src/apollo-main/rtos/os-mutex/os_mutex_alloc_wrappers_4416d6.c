/* Apollo main 0x4416d6/0x4416f0: dynamic and static RTOS mutex wrappers. */
#include <stdint.h>

extern uint32_t audio_os_mutex_dynamic_core_441636(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_os_mutex_static_core_4415ca(uint32_t, uint32_t, uint32_t,
                                                   uint32_t, uint32_t);
extern void audio_os_mutex_register_4416b8(uint32_t);

uint32_t audio_os_mutex_alloc_dynamic_4416d6(uint32_t kind) {
    uint32_t mutex = audio_os_mutex_dynamic_core_441636(1u, 0u, (uint8_t)kind);
    audio_os_mutex_register_4416b8(mutex);
    return mutex;
}

uint64_t audio_os_mutex_alloc_static_4416f0(uint32_t kind, uint32_t memory) {
    uint32_t byte_kind = (uint8_t)kind;
    uint32_t mutex = audio_os_mutex_static_core_4415ca(1u, 0u, 0u,
                                                       memory, byte_kind);
    audio_os_mutex_register_4416b8(mutex);
    return ((uint64_t)byte_kind << 32) | mutex;
}
