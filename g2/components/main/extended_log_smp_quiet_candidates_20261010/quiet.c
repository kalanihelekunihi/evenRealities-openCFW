#include <stdint.h>

typedef struct {
    int32_t (*format)(uint32_t, uint32_t, uint32_t, uint32_t);
    uint32_t (*find_token)(uint32_t, uint32_t);
    void (*output)(uint32_t, uint32_t, uint32_t);
    void (*guard_exit)(void);
    void (*guard_enter)(void);
} g2_log_quiet_providers;

uint32_t g2_log_candidate_postformat(const void *, uint32_t, uint32_t,
                                     uint32_t, uint32_t);

/* Entry-to-return normal SMP logger path with explicit preconditions:
 * state[240]=0 (default module policy 5), state[1]=0 (no module token),
 * all normal-level mask words zero, state[245]=0 and state[32]=0.
 * Format is one of the two smpSmExecute literals. */
void g2_log_candidate_smp_quiet(const g2_log_quiet_providers *p,
                                uint32_t level, uint32_t format_word,
                                uint32_t arguments_word)
{
    volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)0x20070be8u;
    uint32_t level_byte = (uint8_t)level;
    if (state[241] == 0u || state[0] < level_byte || level_byte > 5u)
        return;
    p->guard_enter();
    (void)g2_log_candidate_postformat(p, level_byte, 0u, format_word,
                                      arguments_word);
}
