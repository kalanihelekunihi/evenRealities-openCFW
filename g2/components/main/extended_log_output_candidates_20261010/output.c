#include <stdint.h>

typedef struct {
    void (*submit)(uint32_t buffer, uint32_t length, uint32_t zero,
                   uint32_t level);
    void (*signal)(uint32_t handle, uint32_t one);
} g2_log_output_providers;

/* Complete local body at 0x44aa80..0x44aa98. Transport submission and
 * signal delivery remain lower provider boundaries. */
void g2_log_candidate_output(const g2_log_output_providers *providers,
                             uint32_t buffer, uint32_t length, uint32_t level)
{
    providers->submit(buffer, length, 0u, (uint8_t)level);
    uint32_t handle = *(volatile uint32_t *)(uintptr_t)0x20074570u;
    providers->signal(handle, 1u);
}
