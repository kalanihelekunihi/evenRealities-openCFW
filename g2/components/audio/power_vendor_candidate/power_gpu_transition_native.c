/* Native 0x47f11c GPU mode transition. Live mode bytes, register state and
 * slot-9 platform callback are read at runtime; no product state is seeded. */
#include "power.h"
#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
typedef uint32_t (*g2_gpu_mode_callback)(uint8_t, uint8_t);

static void notify_mode(uint8_t enabled, uint8_t mode) {
    g2_gpu_mode_callback f = *(g2_gpu_mode_callback volatile *)(uintptr_t)0x20073294u;
    if (f) (void)f(enabled, mode);
}

uint32_t g2_power_gpu_mode_select(uint32_t mode) {
    mode=(uint8_t)mode;
    if (mode!=0u && mode!=3u) return 6u;
    if (mode==3u && ((REG(0x40021108u)&0x3fu)>>4)!=3u) return 7u;
    g2_power_descriptor d;
    if (g2_power_get_descriptor(&d,0x14u)!=0u) return 1u;
    /* Native status getter returns a byte; a powered GPU blocks mode change. */
    if ((REG(d.status_register)&d.status_mask)!=0u) return 3u;
    if (mode==g2_power_current_gpu_mode) {
        if (g2_power_previous_gpu_mode!=g2_power_current_gpu_mode)
            g2_power_previous_gpu_mode=(uint8_t)mode;
        return 0u;
    }
    uint32_t saved=g2_power_critical_save();
    if (mode==3u) {
        notify_mode(1u,3u);
        REG(0x40021090u)|=1u;
    } else {
        REG(0x40021090u)&=~1u;
    }
    audio_delay_us(1u);
    REG(0x4002108cu)=(REG(0x4002108cu)&~3u)|(mode&3u);
    g2_power_current_gpu_mode=(uint8_t)mode;
    g2_power_previous_gpu_mode=(uint8_t)mode;
    audio_delay_us(6u);
    if (mode==0u) notify_mode(1u,0u);
    g2_power_critical_restore(saved);
    return 0u;
}
