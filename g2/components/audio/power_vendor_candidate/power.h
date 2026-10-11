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
extern volatile uint32_t g2_power_current_gpu_mode;
extern volatile uint32_t g2_power_previous_gpu_mode;
extern uint32_t g2_power_get_descriptor(g2_power_descriptor *, uint32_t);
extern void g2_power_tempco_postpone(void);
extern void g2_power_tempco_pending(void);
extern uint32_t g2_power_spot_update(uint32_t, bool, void *);
extern uint32_t g2_power_gpu_mode_select(uint32_t);
extern void g2_power_clock_request(uint32_t, uint32_t);
extern void g2_power_clock_release(uint32_t, uint32_t);
extern void g2_power_clock_release_all(uint32_t);
extern uint32_t g2_power_critical_save(void);
extern void g2_power_critical_restore(uint32_t);
extern uint32_t g2_power_wait_status(uint32_t, uintptr_t, uint32_t, uint32_t, bool);
extern void g2_power_delay_us(uint32_t);
uint32_t g2_power_vendor_enable(uint32_t);
uint32_t g2_power_vendor_disable(uint32_t);
#endif
