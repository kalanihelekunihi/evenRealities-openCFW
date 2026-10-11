#include <stdint.h>

#define SMP_BASE ((volatile uint8_t *)(uintptr_t)0x20070aecu)
typedef struct {
    uint32_t state_rows;
    uint32_t handlers;
    uint32_t fallback;
} g2_smp_transition_group;
typedef struct { uint32_t (*conn_role)(uint32_t conn_id); } g2_smp_role_provider;

/* Stock tail 0x56f0ec..0x56f144, after logging. */
void g2_smp_candidate_dispatch_tail(void *context, uint32_t ccb_word,
                                    uint32_t message_word)
{
    const g2_smp_role_provider *p = (const g2_smp_role_provider *)context;
    volatile uint8_t *ccb = (volatile uint8_t *)(uintptr_t)ccb_word;
    volatile uint8_t *message = (volatile uint8_t *)(uintptr_t)message_word;
    uint32_t role = p->conn_role(ccb[61]);
    uint32_t group_word = *(volatile uint32_t *)(uintptr_t)(
        (uint32_t)(uintptr_t)SMP_BASE + (role == 1u ? 228u : 232u));
    volatile g2_smp_transition_group *group =
        (volatile g2_smp_transition_group *)(uintptr_t)group_word;
    uint32_t row_word = *(volatile uint32_t *)(uintptr_t)(
        group->state_rows + (uint32_t)ccb[62] * 4u);
    volatile uint8_t *triple = (volatile uint8_t *)(uintptr_t)row_word;
    volatile uint8_t *fallback = (volatile uint8_t *)(uintptr_t)group->fallback;
    for (;;) {
        if (triple[0] == message[2]) {
            ccb[62] = triple[1];
            uint32_t handler_word = *(volatile uint32_t *)(uintptr_t)(
                group->handlers + (uint32_t)triple[2] * 4u);
            ((void (*)(uint32_t, uint32_t))(uintptr_t)handler_word)(ccb_word,
                                                                   message_word);
            return;
        }
        triple += 3;
        if (triple[0] != 0u) continue;
        if (triple == fallback + 12) return;
        triple = fallback;
    }
}
