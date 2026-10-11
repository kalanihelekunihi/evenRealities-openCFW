#include <stdint.h>

/* Native source 0x0058fdbc..0x0059005d. It programs clock source and
 * bit timing for either I2S instance using the authenticated MMIO base. */
extern void g2_codec_source_mux(uint32_t instance, uint32_t mode); /* 0x58fd7e */

void audio_power_reconfigure(uint32_t instance, uint32_t source) {
    volatile uint32_t *const mmio = (volatile uint32_t *)(uintptr_t)
        (0x40208000u + (instance << 12));
    volatile uint32_t *const control = &mmio[0x100u / 4u];
    uint32_t const source_class = (source >> 16) & 0xffu;
    uint32_t const divider = (source >> 8) & 0xffu;
    uint32_t const low = source & 0xffu;
    if (source_class == 1u) {
        mmio[0x54u / 4u] |= 1u;
        uint32_t const prior_clock = *control;
        *control &= ~0x1000u;
        *control = (*control & ~0x00070000u) | ((source & 7u) << 16);
        *control = (*control & ~0x1000u) | (prior_clock & 0x1000u);
        uint32_t const prior_enable = *control;
        *control &= ~1u;
        *control = (*control & ~0x1f0u) | 0x170u;
        *control = (*control & ~1u) | (prior_enable & 1u);
        return;
    }

    mmio[0x54u / 4u] &= ~1u;
    uint32_t const prior_clock = *control;
    *control &= ~0x1000u;
    *control = (*control & ~0x00070000u) | 0x40000u;
    *control = (*control & ~0x1000u) | (prior_clock & 0x1000u);
    uint32_t const requested = (*control & 0x1ffu) >> 4;
    uint32_t const clocks = *(volatile const uint32_t *)(uintptr_t)0x400204e8u;
    uint32_t const current = (clocks >> (instance == 0u ? 5u : 7u)) & 3u;
    if (divider == current) {
        if (divider == 2u && requested != low) {
            uint32_t const prior_enable = *control;
            *control &= ~1u;
            *control = (*control & ~0x1f0u) | ((source & 0x1fu) << 4);
            *control = (*control & ~1u) | (prior_enable & 1u);
        }
        return;
    }
    uint32_t const prior_enable = *control;
    *control |= 1u;
    if (requested == 0x17u) {
        uint32_t const enabled = *control;
        *control &= ~1u;
        *control = (*control & ~0x1f0u) | 0xa0u;
        *control = (*control & ~1u) | (enabled & 1u);
    }
    if (current == 2u) {
        g2_codec_source_mux(instance, 0u);
        uint32_t const enabled = *control;
        *control &= ~1u;
        *control = (*control & ~0x1f0u) | 0x170u;
        *control = (*control & ~1u) | (enabled & 1u);
    } else if (current == 0u || current == 1u) {
        if (divider == 2u) {
            g2_codec_source_mux(instance, 2u);
            uint32_t const enabled = *control;
            *control &= ~1u;
            *control = (*control & ~0x1f0u) | ((source & 0x1fu) << 4);
            *control = (*control & ~1u) | (enabled & 1u);
        } else {
            g2_codec_source_mux(instance, 0u);
        }
    }
    *control = (*control & ~1u) | (prior_enable & 1u);
}

void audio_i2s_reconfigure(uint32_t instance, uint32_t source)
    __attribute__((alias("audio_power_reconfigure")));
