/* Authenticated Apollo Main power ABI constants and ROM literal targets.
 * Live MMIO and GPU-mode RAM are read at runtime; this object supplies only
 * source-owned immutable selectors, masks and addresses. */
#include "power.h"

const g2_power_product_config g2_power_product = {
    .crypto=0x17u,.otp=0x1du,.debug=0x1cu,.gfx=0x14u,.pdm0=0x1eu,
    .monitor_device_mask=0x3fffffffu,.monitor_audio_mask=0x4c4u,
    .status_success=0u,.status_fail=1u,.status_in_use=3u,
    .max_wait_us=5u,.max_wait_otp_us=100000u,.crypto_wait_us=100u,
    .stim_device=3u,.stim_audio=4u,.stim_gpu=1u,
    .gpu_low_power=0u,.gpu_high_performance=3u,
    .gpu_active_lp=1u,.gpu_active_hp=2u,.gpu_off=0u,
    .clk_hfrc=4u,.clk_hfrc2=5u,.user_gfx=0x14u,.user_crypto=0x17u,
    .otp_power_status_register=0x40021008u,
    .crypto_nvm_idle_register=0x400c1f10u,
    .otp_ptm_status_register=0x40014ac4u,
    .revision_register=0x4002000cu,
    .debug_demcr_register=0xe000edfcu,
    .debug_control_register=0x40020250u,
    .otp_power_mask=0x08000000u,.crypto_power_mask=0x00200000u,
    .crypto_nvm_idle_mask=1u,.otp_ptm_busy_mask=1u,
    .debug_trcena_mask=0x01000000u,
    .debug_trace_enable_mask=1u,.debug_clock_select_mask=14u,
    .min_revision_for_otp_crypto_off=0x22u,
    .shared={{0x1eu,0x1eu},{0xc0u,0xc0u},{0x1e0u,0x1e0u},
             {0x1e00u,0x1e00u},{0x30000001u,0x30000001u}},
};
