#ifndef G2_POWER_VENDOR_CANDIDATE_H
#define G2_POWER_VENDOR_CANDIDATE_H
#include <stdbool.h>
#include <stdint.h>
typedef struct {
    uintptr_t enable_register, status_register;
    uint32_t enable_mask, status_mask;
} g2_power_descriptor;
typedef struct {
    uint32_t crypto, otp, debug, gfx, pdm0;
    uint32_t monitor_device_mask, monitor_audio_mask;
    uint32_t status_success, status_fail, status_in_use;
    uint32_t max_wait_us, max_wait_otp_us, crypto_wait_us;
    uint32_t stim_device, stim_audio, stim_gpu;
    uint32_t gpu_low_power, gpu_high_performance, gpu_active_lp, gpu_active_hp, gpu_off;
    uint32_t clk_hfrc, clk_hfrc2, user_gfx, user_crypto;
    uintptr_t otp_power_status_register, crypto_nvm_idle_register, otp_ptm_status_register;
    uintptr_t revision_register, debug_demcr_register, debug_control_register;
    uint32_t otp_power_mask, crypto_power_mask, crypto_nvm_idle_mask, otp_ptm_busy_mask;
    uint32_t debug_trcena_mask, debug_trace_enable_mask, debug_clock_select_mask;
    uint8_t min_revision_for_otp_crypto_off;
    struct { uint32_t status_mask, enable_group_mask; } shared[5];
} g2_power_product_config;
/* Product-specific configuration and state must be supplied by an attributed
 * binding. No fallback constants or success-only hooks are defined here. */
extern const g2_power_product_config g2_power_product;
/* Native ROM pointers at 0x47fac0/c4 target adjacent live byte cells. */
#define g2_power_current_gpu_mode (*(volatile uint8_t *)(uintptr_t)0x20074f60u)
#define g2_power_previous_gpu_mode (*(volatile uint8_t *)(uintptr_t)0x20074f61u)
extern uint32_t g2_power_get_descriptor(g2_power_descriptor *, uint32_t);
extern uint32_t g2_power_tempco_postpone(void);
extern uint32_t g2_power_tempco_pending(void);
/* These selected bodies map by native entry 0x480312/0x4c44bc/0x4c4530/
 * 0x4c45a4, respectively. Their returns are ignored by this caller. */
extern uint32_t audio_ble_flash_control(uint32_t, uint32_t, const uint32_t *);
extern uint32_t g2_power_gpu_mode_select(uint32_t);
extern uint32_t audio_uart_pin_mux_enable(uint32_t, uint32_t);
extern uint32_t audio_uart_pin_mux_disable(uint32_t, uint32_t);
extern uint32_t audio_uart_font_pin_mux_disable(uint32_t);
extern uint32_t g2_power_critical_save(void);
extern void g2_power_critical_restore(uint32_t);
/* Stock 0x480826/0x4807fc/0x4807a0 are already selected as these
 * source-defined timing bodies. The fifth wait argument is the polarity. */
extern uint32_t audio_wait5(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_wait4(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_delay_us(uint32_t);
uint32_t g2_power_vendor_enable(uint32_t);
uint32_t g2_power_vendor_disable(uint32_t);
#endif
