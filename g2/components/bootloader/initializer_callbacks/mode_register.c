/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static inline uint32_t critical_save(void)
{
    uint32_t previous;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(previous) :: "memory");
    return previous;
}

static inline void critical_restore(uint32_t previous)
{
    __asm__ volatile("msr primask, %0" :: "r"(previous) : "memory");
}

/* Reconstructed 0x41d9aa: set/toggle one interrupt-controller bit.  Register
 * addresses are the literal fixed register banks used by the locked body.
 */
uint32_t opencfw_bl_mode_register_update(uint32_t identifier,
                                         uint32_t mode,
                                         uint32_t unused)
{
    (void)unused;
    const uint32_t id = identifier & 0xffu;
    const uint32_t word = (id >> 5) & 7u;
    const uint32_t bit = 1u << (id & 31u);
    volatile uint32_t *const set_bank[6] = {
        (volatile uint32_t *)0x40010458u,
        (volatile uint32_t *)0x4001043cu,
        (volatile uint32_t *)0x40010420u,
        (volatile uint32_t *)0x400104acu,
        (volatile uint32_t *)0x40010490u,
        (volatile uint32_t *)0x40010474u,
    };

    switch (mode & 0xffu) {
    case 0u:
    case 1u:
    case 3u:
    case 4u:
        set_bank[mode & 0xffu][word] = bit;
        break;
    case 2u:
    case 5u: {
        const uint32_t previous = critical_save();
        set_bank[mode & 0xffu][word] ^= bit;
        critical_restore(previous);
        break;
    }
    default:
        break;
    }
    return 0u;
}
