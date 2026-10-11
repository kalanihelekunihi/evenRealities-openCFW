#include <stdint.h>

extern uint32_t g2_codec_clock_mux_request(uint32_t source,
                                            uint32_t delay_us); /* 0x539bbc */

/* Native 0x591d56..0x591d79. */
void g2_pdm_mux(uint32_t instance, uint32_t source) {
    (void)instance;
    (void)g2_codec_clock_mux_request(source <= 2u ? source : 2u, 2u);
}

static void switch_field(volatile uint32_t *reg, uint32_t value) {
    const uint32_t enabled = *reg & 1u;
    *reg &= ~1u;
    *reg = (*reg & ~0xeu) | ((value & 7u) << 1);
    *reg = (*reg & ~1u) | enabled;
}

/* Native 0x591d7a..0x591fab, including revision-dependent mux transitions. */
void g2_pdm_clock_select(uint32_t instance, int32_t clock_mode) {
    const uint16_t setting = (uint16_t)clock_mode;
    const uint32_t source = (setting >> 8) & 0xffu;
    const uint32_t selected = setting & 0xffu;
    volatile uint32_t *const reg = (volatile uint32_t *)(uintptr_t)
        (0x40201000u + (instance << 12));
    const uint32_t revision =
        *(volatile uint32_t *)(uintptr_t)0x400204e8u & 3u;
    const uint32_t current = (*reg >> 1) & 7u;

    if (source == revision) {
        if (source == 2u && current != selected)
            switch_field(reg, selected);
        return;
    }

    const uint32_t enabled = *reg & 1u;
    *reg |= 1u;
    if (revision == 2u) {
        if (current == 6u)
            switch_field(reg, 2u);
        g2_pdm_mux(instance, source);
        switch_field(reg, 6u);
    } else if (revision == 0u) {
        if (source == 2u) {
            if (current == 6u)
                switch_field(reg, 2u);
            g2_pdm_mux(instance, 2u);
            switch_field(reg, selected);
        } else if (source == 1u) {
            g2_pdm_mux(instance, 1u);
        }
    } else if (revision == 1u) {
        volatile uint32_t *const mode =
            (volatile uint32_t *)(uintptr_t)0x400200c0u;
        *mode |= 1u;
        if (source == 2u) {
            if (current == 6u)
                switch_field(reg, 2u);
            g2_pdm_mux(instance, 2u);
            switch_field(reg, selected);
        } else if (source == 0u) {
            g2_pdm_mux(instance, 0u);
        }
        *mode &= ~1u;
    }
    *reg = (*reg & ~1u) | enabled;
}
