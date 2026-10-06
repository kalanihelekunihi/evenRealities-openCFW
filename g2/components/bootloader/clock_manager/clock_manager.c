/* Readable reconstruction of the two private clock-manager dispatchers.
 * Clock-specific providers remain platform services. */
#include "clock_manager.h"

extern uint32_t opencfw_bl_clock_request_id0(uint8_t user_id);
extern uint32_t opencfw_bl_clock_request_id1(uint8_t user_id);
extern uint32_t opencfw_bl_clock_request_id2(uint8_t user_id);
extern uint32_t opencfw_bl_clock_request_id3(uint8_t user_id);
extern uint32_t opencfw_bl_clock_request_id4(uint8_t user_id);
extern uint32_t opencfw_bl_clock_request_id5(uint8_t user_id);
extern uint32_t opencfw_bl_clock_request_id6(uint8_t user_id);

extern uint32_t opencfw_bl_clock_release_id0(uint8_t user_id);
extern uint32_t opencfw_bl_clock_release_id1(uint8_t user_id);
extern uint32_t opencfw_bl_clock_release_id2(uint8_t user_id);
extern uint32_t opencfw_bl_clock_release_id3(uint8_t user_id);
extern uint32_t opencfw_bl_clock_release_id4(uint8_t user_id);
extern uint32_t opencfw_bl_clock_release_id5(uint8_t user_id);
extern uint32_t opencfw_bl_clock_release_id6(uint8_t user_id);

enum {
    CLOCK_CLASS_COUNT = 7u,
    CLOCK_USER_COUNT = 57u,
    CLOCK_USER_BITS_BASE = 0x20026e74u
};

static volatile uint32_t *clock_user_word(uint8_t clock_id, uint8_t user_id)
{
    const uint32_t word_index = (uint32_t)clock_id * 2u +
                                ((uint32_t)user_id >> 5);
    return (volatile uint32_t *)(uintptr_t)(CLOCK_USER_BITS_BASE +
                                            word_index * 4u);
}

static uint32_t clock_user_has(uint8_t clock_id, uint8_t user_id)
{
    const uint32_t mask = 1u << (user_id & 31u);
    return (*clock_user_word(clock_id, user_id) & mask) != 0u;
}

static uint32_t clock_user_update(uint8_t clock_id, uint8_t user_id,
                                  uint32_t request)
{
    if (clock_id >= CLOCK_CLASS_COUNT || user_id >= CLOCK_USER_COUNT)
        return 6u;
    volatile uint32_t *const word = clock_user_word(clock_id, user_id);
    const uint32_t mask = 1u << (user_id & 31u);
    if (request)
        *word |= mask;
    else
        *word &= ~mask;
    return 0u;
}

static uint32_t clock_critical_save_disable(void)
{
    uint32_t previous;
    __asm volatile("mrs %0, primask\n\tcpsid i"
                   : "=r"(previous) :: "memory");
    return previous;
}

static void clock_critical_restore(uint32_t previous)
{
    __asm volatile("msr primask, %0" :: "r"(previous) : "memory");
}

/* Recovered provider pair 0x421a30/0x421a62. This clock class has only the
 * per-user bookkeeping path; it makes no clock-tree MMIO writes. */
uint32_t opencfw_bl_clock_request_id0(uint8_t user_id)
{
    if (clock_user_has(0u, user_id))
        return 0u;
    const uint32_t previous = clock_critical_save_disable();
    (void)clock_user_update(0u, user_id, 1u);
    clock_critical_restore(previous);
    return 0u;
}

uint32_t opencfw_bl_clock_release_id0(uint8_t user_id)
{
    if (!clock_user_has(0u, user_id))
        return 0u;
    const uint32_t previous = clock_critical_save_disable();
    (void)clock_user_update(0u, user_id, 0u);
    clock_critical_restore(previous);
    return 0u;
}

uint32_t clock_request(uint32_t clock_id_register, uint32_t user_id_register)
{
    const uint8_t clock_id = (uint8_t)clock_id_register;
    const uint8_t user_id = (uint8_t)user_id_register;
    if (user_id >= 0x39u)
        return 6u;

    switch (clock_id) {
    case 0u: return opencfw_bl_clock_request_id0(user_id);
    case 1u: return opencfw_bl_clock_request_id1(user_id);
    case 2u: return opencfw_bl_clock_request_id2(user_id);
    case 3u: return opencfw_bl_clock_request_id3(user_id);
    case 4u: return opencfw_bl_clock_request_id4(user_id);
    case 5u: return opencfw_bl_clock_request_id5(user_id);
    case 6u: return opencfw_bl_clock_request_id6(user_id);
    default: return 6u;
    }
}

uint32_t clock_release(uint32_t clock_id_register, uint32_t user_id_register)
{
    const uint8_t clock_id = (uint8_t)clock_id_register;
    const uint8_t user_id = (uint8_t)user_id_register;
    if (user_id >= 0x39u)
        return 6u;

    switch (clock_id) {
    case 0u: return opencfw_bl_clock_release_id0(user_id);
    case 1u: return opencfw_bl_clock_release_id1(user_id);
    case 2u: return opencfw_bl_clock_release_id2(user_id);
    case 3u: return opencfw_bl_clock_release_id3(user_id);
    case 4u: return opencfw_bl_clock_release_id4(user_id);
    case 5u: return opencfw_bl_clock_release_id5(user_id);
    case 6u: return opencfw_bl_clock_release_id6(user_id);
    default: return 6u;
    }
}
