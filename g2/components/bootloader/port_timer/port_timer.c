/* Readable source reconstruction of the bootloader's local STIMER port.
 * Constants are pinned to the authenticated image's literal pools. */
#include "port_timer.h"

#include <stddef.h>

enum {
    PORT_STIMER_BASE = 0x40008800u,
    PORT_STIMER_COUNTER = PORT_STIMER_BASE + 0x04u,
    PORT_STIMER_COMPARE0 = PORT_STIMER_BASE + 0x20u,
    PORT_TIMER_GATE_OR_REGISTER = 0x40008900u,
    PORT_NVIC_ISER = 0xe000e100u,
    PORT_NVIC_IPR = 0xe000e400u,
    PORT_NVIC_IPR_NEGATIVE_BASE = 0xe000ed18u,
    PORT_COMPARE_SHADOW = 0x200001c8u,
    PORT_TIMER_START = 0x20027120u,
    PORT_TIMER_INTERVAL = 0x20027124u,
    PORT_TIMER_MAX_INTERVAL = 0x20027128u,
    PORT_TIMER_READY = 0x200271bfu,
    PORT_TIMER_CONFIGURED_VALUE = 0x20u,
    PORT_TIMER_IRQ_NUMBER = 32u,
    PORT_TIMER_CLOCK_USER = 0x32u,
    PORT_COMPARE_COUNT = 8u,
    PORT_COMPARE_LATE_STATUS = 0x08000000u
};

_Static_assert(PORT_STIMER_COUNTER == 0x40008804u,
               "Apollo510 STIMER counter address");
_Static_assert(PORT_STIMER_COMPARE0 == 0x40008820u,
               "Apollo510 STIMER compare-A address");

static inline volatile uint32_t *reg32(uint32_t address)
{
    return (volatile uint32_t *)(uintptr_t)address;
}

static inline uint32_t primask_save_disable(void)
{
    uint32_t saved;
    __asm volatile("mrs %0, primask\n\tcpsid i"
                   : "=r"(saved) :: "memory");
    return saved;
}

static inline void primask_restore(uint32_t saved)
{
    __asm volatile("msr primask, %0" :: "r"(saved) : "memory");
}

static uint32_t clock_source_class(uint32_t selector)
{
    uint32_t adjusted = selector - 1u;
    if (adjusted <= 1u)
        return 4u;
    if (adjusted == 5u)
        return 0u;
    return 7u;
}

void opencfw_bl_port_timer_gate_enable(uint32_t bits)
{
    *reg32(PORT_TIMER_GATE_OR_REGISTER) |= bits;
}

void opencfw_bl_port_timer_irq_priority(int32_t irq, int32_t priority)
{
    const int16_t irq16 = (int16_t)irq;
    volatile uint8_t *destination;
    if (irq16 < 0) {
        destination = (volatile uint8_t *)(uintptr_t)
            (PORT_NVIC_IPR_NEGATIVE_BASE + ((uint16_t)irq16 & 0x0fu) - 4u);
    } else {
        destination = (volatile uint8_t *)(uintptr_t)
            (PORT_NVIC_IPR + (uint16_t)irq16);
    }
    *destination = (uint8_t)((uint32_t)priority << 4);
}

void opencfw_bl_port_timer_irq_enable(int32_t irq)
{
    const int16_t irq16 = (int16_t)irq;
    if (irq16 >= 0) {
        *reg32(PORT_NVIC_ISER + ((uint32_t)(uint16_t)irq16 >> 5) * 4u) =
            1u << ((uint16_t)irq16 & 0x1fu);
    }
}

uint32_t opencfw_bl_port_timer_clock_configure(uint32_t value)
{
    volatile uint32_t *const clock_config = reg32(PORT_STIMER_BASE);
    const uint32_t old = *clock_config;
    const uint32_t next_source = value & 0x0fu;
    const uint32_t old_source = old & 0x0fu;
    const uint32_t next_class = clock_source_class(next_source);
    const uint32_t old_class = clock_source_class(old_source);
    uint32_t request_new;
    uint32_t release_old;

    if ((value & 0xc0000000u) == 0u) {
        if ((old & 0xc0000000u) == 0u) {
            request_new = next_class != old_class;
            release_old = next_class != old_class;
        } else {
            request_new = 1u;
            release_old = 0u;
        }
    } else {
        request_new = 0u;
        release_old = 1u;
    }

    if (request_new && next_source != 0u && next_source < 7u)
        (void)clock_request((uint8_t)next_class,
                            (uint8_t)PORT_TIMER_CLOCK_USER);

    *clock_config = value;

    if (release_old && old_source != 0u && old_source < 7u)
        (void)clock_release((uint8_t)old_class,
                            (uint8_t)PORT_TIMER_CLOCK_USER);

    *(volatile uint8_t *)(uintptr_t)PORT_TIMER_READY = 1u;
    return old;
}

__attribute__((noinline))
uint32_t opencfw_bl_port_timer_read_counter(void)
{
    uint32_t samples[3];
    const uint32_t saved = primask_save_disable();
    samples[0] = *reg32(PORT_STIMER_COUNTER);
    samples[1] = *reg32(PORT_STIMER_COUNTER);
    samples[2] = *reg32(PORT_STIMER_COUNTER);
    primask_restore(saved);
    return samples[0] == samples[1] ? samples[1] : samples[2];
}

uint32_t opencfw_bl_port_timer_compare_set(uint32_t compare_id,
                                           uint32_t delta)
{
    uint32_t start = opencfw_bl_port_timer_read_counter();
    uint32_t probe = start;
    uint32_t now;
    uint32_t saved;
    uint32_t compare_value;
    uint32_t status = 0u;
    volatile uint32_t *const software_compare =
        reg32(PORT_COMPARE_SHADOW + compare_id * 4u);

    if (compare_id >= PORT_COMPARE_COUNT)
        return 5u;

    while (probe == *software_compare || probe == *software_compare + 1u)
        probe = opencfw_bl_port_timer_read_counter();

    saved = primask_save_disable();
    now = opencfw_bl_port_timer_read_counter();
    if ((now - start) + 3u < delta) {
        compare_value = start + (delta - now) - 3u;
    } else {
        compare_value = 1u;
        status = PORT_COMPARE_LATE_STATUS;
    }

    *reg32(PORT_STIMER_COMPARE0 + compare_id * 4u) = compare_value;
    *software_compare = opencfw_bl_port_timer_read_counter();
    primask_restore(saved);
    return status;
}

uint32_t opencfw_bl_port_timer_configure(void)
{
    uint32_t incoming_r3;
    uint32_t old_clock;
    volatile uint32_t *const interval = reg32(PORT_TIMER_INTERVAL);
    __asm volatile("mov %0, r3" : "=r"(incoming_r3));

    *interval = PORT_TIMER_CONFIGURED_VALUE;
    *reg32(PORT_TIMER_MAX_INTERVAL) = 0xffffffffu / *interval - 4u;
    opencfw_bl_port_timer_gate_enable(1u);
    opencfw_bl_port_timer_irq_priority((int32_t)PORT_TIMER_IRQ_NUMBER, 0xff);
    opencfw_bl_port_timer_irq_enable((int32_t)PORT_TIMER_IRQ_NUMBER);
    old_clock = opencfw_bl_port_timer_clock_configure(0x80000000u);
    *reg32(PORT_TIMER_START) = opencfw_bl_port_timer_read_counter();
    (void)opencfw_bl_port_timer_compare_set(0u, *interval);
    (void)opencfw_bl_port_timer_clock_configure(
        (old_clock & 0x7ffffff0u) | 0x103u);
    return incoming_r3;
}
