/* Experimental full branch projection of pinned Ambiq Apollo510
 * am_hal_pwrctrl_periph_enable/disable. See README for provenance and limits. */
#include "power.h"
#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))

static bool last_in_domain(uint32_t peripheral) {
    g2_power_descriptor p;
    if (g2_power_get_descriptor(&p, peripheral) != g2_power_product.status_success) return true;
    for (unsigned i = 0; i < 5; ++i) {
        if (p.status_mask == g2_power_product.shared[i].status_mask) {
            uint32_t enabled = REG(p.enable_register);
            return !((enabled & g2_power_product.shared[i].enable_group_mask) &&
                     !(enabled & p.enable_mask));
        }
    }
    return true;
}

uint32_t g2_power_vendor_enable(uint32_t peripheral) {
    peripheral=(uint8_t)peripheral; /* Native public ABI consumes the low byte. */
    const g2_power_product_config *c = &g2_power_product;
    g2_power_descriptor p;
    uint32_t status = g2_power_get_descriptor(&p, peripheral);
    if (status != c->status_success) return status;
    if (REG(p.enable_register) & p.enable_mask) return c->status_success;
    if (peripheral == c->crypto && !(REG(c->otp_power_status_register) & c->otp_power_mask))
        return c->status_fail;
    g2_power_tempco_postpone();
    if (peripheral == c->gfx) {
        if (g2_power_previous_gpu_mode == c->gpu_high_performance)
            (void)g2_power_gpu_mode_select(c->gpu_high_performance);
        (void)audio_uart_pin_mux_enable(c->clk_hfrc, c->user_gfx);
        if (g2_power_current_gpu_mode == c->gpu_high_performance)
            (void)audio_uart_pin_mux_enable(c->clk_hfrc2, c->user_gfx);
        uint32_t gpu_state = g2_power_current_gpu_mode == c->gpu_low_power ?
                             c->gpu_active_lp : c->gpu_active_hp;
        /* Native 0x47f642 continues after the GPU SPOT callback as well. */
        (void)audio_ble_flash_control(c->stim_gpu, 1u, &gpu_state);
    } else {
        if ((p.enable_mask & c->monitor_device_mask) && peripheral < c->pdm0) {
            /* Stock 0x47f660 calls the ordinary SPOT hook and continues. */
            (void)audio_ble_flash_control(c->stim_device, 1u, &p.status_mask);
        }
        if ((p.enable_mask & c->monitor_audio_mask) && peripheral >= c->pdm0) {
            /* Stock 0x47f67c likewise ignores the audio hook result. */
            (void)audio_ble_flash_control(c->stim_audio, 1u, &p.status_mask);
        }
    }
    uint32_t saved = g2_power_critical_save();
    REG(p.enable_register) |= p.enable_mask;
    g2_power_critical_restore(saved);
    g2_power_tempco_pending();
    status = audio_wait5(c->max_wait_us, (uint32_t)p.status_register,
                         p.status_mask, p.status_mask, 1);
    if (status != c->status_success) return status;
    if (peripheral == c->crypto) {
        status = audio_wait4(c->crypto_wait_us, (uint32_t)c->crypto_nvm_idle_register,
                             c->crypto_nvm_idle_mask, c->crypto_nvm_idle_mask);
        if (status != c->status_success) return status;
        (void)audio_uart_pin_mux_enable(c->clk_hfrc, c->user_crypto);
    }
    if (peripheral == c->otp) audio_delay_us(100);
    return REG(p.status_register) & p.status_mask ? c->status_success : c->status_fail;
}

uint32_t g2_power_vendor_disable(uint32_t peripheral) {
    peripheral=(uint8_t)peripheral;
    const g2_power_product_config *c = &g2_power_product;
    g2_power_descriptor p;
    uint32_t status = g2_power_get_descriptor(&p, peripheral);
    if (status != c->status_success) return status;
    if (!(REG(p.enable_register) & p.enable_mask)) return c->status_success;
    if (peripheral == c->otp) {
        if ((REG(c->revision_register) & 0xffu) < c->min_revision_for_otp_crypto_off &&
            (REG(c->otp_power_status_register) & c->crypto_power_mask))
            return c->status_in_use;
        status = audio_wait5(c->max_wait_otp_us, (uint32_t)c->otp_ptm_status_register,
                             c->otp_ptm_busy_mask, 0, 1);
        if (status != c->status_success) return status;
    }
    if (peripheral == c->debug) {
        REG(c->debug_demcr_register) &= ~c->debug_trcena_mask;
        /* Native performs two control-register transactions in this order. */
        REG(c->debug_control_register) &= ~c->debug_trace_enable_mask;
        REG(c->debug_control_register) &= ~c->debug_clock_select_mask;
    }
    g2_power_tempco_postpone();
    uint32_t saved = g2_power_critical_save();
    REG(p.enable_register) &= ~p.enable_mask;
    g2_power_critical_restore(saved);
    if (last_in_domain(peripheral)) {
        status = audio_wait5(c->max_wait_us, (uint32_t)p.status_register,
                             p.status_mask, p.status_mask, 0);
        if (status == c->status_success) {
            if (peripheral == c->crypto)
                (void)audio_uart_pin_mux_disable(c->clk_hfrc, c->user_crypto);
            if (peripheral == c->gfx) {
                uint32_t gpu_state = c->gpu_off;
                if (g2_power_current_gpu_mode == c->gpu_high_performance) {
                    (void)g2_power_gpu_mode_select(c->gpu_low_power);
                    g2_power_previous_gpu_mode = c->gpu_high_performance;
                } else {
                    g2_power_previous_gpu_mode = c->gpu_low_power;
                }
                /* Native 0x47f8c8 retains the wait result, even on callback failure. */
                (void)audio_ble_flash_control(c->stim_gpu, 1u, &gpu_state);
                (void)audio_uart_font_pin_mux_disable(c->user_gfx);
            } else {
                if (peripheral < c->pdm0 && (p.enable_mask & c->monitor_device_mask)) {
                    /* Stock 0x47f8e4 continues through TEMPco pending. */
                    (void)audio_ble_flash_control(c->stim_device, 0u, &p.status_mask);
                }
                if (peripheral >= c->pdm0 && (p.enable_mask & c->monitor_audio_mask)) {
                    /* Stock 0x47f8fe also ignores this callback result. */
                    (void)audio_ble_flash_control(c->stim_audio, 0u, &p.status_mask);
                }
            }
        }
    }
    g2_power_tempco_pending();
    return status;
}

/* Receipt address maps bind these enable names to stock 0x47f5b8
 * and disable names to 0x47f7ae. These aliases select this explicitly
 * experimental vendor-derived body without implying stock equivalence. */
uint32_t am_hal_pwrctrl_periph_enable(uint32_t) __attribute__((alias("g2_power_vendor_enable")));
uint32_t stock_enable(uint32_t) __attribute__((alias("g2_power_vendor_enable")));
uint32_t stock_peripheral_enable(uint32_t) __attribute__((alias("g2_power_vendor_enable")));
uint32_t audio_power_peripheral_on(uint32_t) __attribute__((alias("g2_power_vendor_enable")));
uint32_t am_hal_pwrctrl_periph_disable(uint32_t) __attribute__((alias("g2_power_vendor_disable")));
uint32_t stock_disable(uint32_t) __attribute__((alias("g2_power_vendor_disable")));
uint32_t audio_power_peripheral_off(uint32_t) __attribute__((alias("g2_power_vendor_disable")));
