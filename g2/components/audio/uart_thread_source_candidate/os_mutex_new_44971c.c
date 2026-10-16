/* Apollo main 0x44971c: CMSIS osMutexNew wrapper. */
#include <stdint.h>

struct audio_os_mutex_attr {
    uint32_t name;
    uint32_t flags;
    uint32_t cb_mem;
    uint32_t cb_size;
};
_Static_assert(sizeof(struct audio_os_mutex_attr) == 16u, "mutex attribute ABI");

extern uint32_t audio_os_irq_context_44900e(void);
extern uint32_t audio_os_mutex_alloc_dynamic_4416d6(uint32_t);
extern uint32_t audio_os_mutex_alloc_static_4416f0(uint32_t, uint32_t);

uint32_t audio_even_ai_mutex_create_44971c(const struct audio_os_mutex_attr *attr) {
    if (audio_os_irq_context_44900e() != 0u) return 0u;
    uint32_t flags = attr == 0 ? 0u : attr->flags;
    if ((flags & 8u) != 0u) return 0u;
    uint32_t kind = (flags & 1u) != 0u ? 4u : 1u;
    uint32_t result = 0u;
    if (attr == 0 || (attr->cb_mem == 0u && attr->cb_size == 0u))
        result = audio_os_mutex_alloc_dynamic_4416d6(kind);
    else if (attr->cb_mem != 0u && attr->cb_size >= 80u)
        result = audio_os_mutex_alloc_static_4416f0(kind, attr->cb_mem);
    if (result != 0u && (flags & 1u) != 0u) result |= 1u;
    return result;
}
