#include <stdint.h>

typedef struct {
    void (*guard_enter)(void);
    void (*guard_exit)(void);
} g2_log_module_policy_providers;

uint32_t g2_smp_candidate_compare(void *, uint32_t, uint32_t, uint32_t);

/* Non-null module branch of 0x43d4b0..0x43d574. Five 33-byte RAM rows,
 * active byte at +81, level at +49, name bytes at +50. */
uint32_t g2_log_candidate_module_policy(const g2_log_module_policy_providers *p,
                                        uint32_t module_word)
{
    volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)0x20070be8u;
    if (state[240] == 0u) return 5u;
    p->guard_enter();
    uint32_t result = 5u;
    for (uint32_t i=0u;i<5u;i++) {
        uint32_t row=(uint32_t)(uintptr_t)state+i*33u;
        if (*(volatile uint8_t *)(uintptr_t)(row+81u) != 1u) continue;
        if (g2_smp_candidate_compare((void *)0,module_word,row+50u,30u)!=0u)
            continue;
        result=*(volatile uint8_t *)(uintptr_t)(row+49u);
        break;
    }
    p->guard_exit();
    return result;
}
