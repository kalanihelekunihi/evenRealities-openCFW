/* GPU bring-up for the NemaGFX / NemaVG renderer (no source path retained).
 * Native 0x59fae0..0x59fb62; literal pool 0x59fb64..0x59fb6c.
 *
 * Called once from the board init sequence at 0x5cdd14 (after the CPU is put in
 * high-performance mode): power-cycles the GPU domain into HP mode, initialises
 * NemaGFX, gives NemaVG a 576x288 stencil with a zeroed (driver-allocated)
 * nema_buffer_t, then hands the GPU to the deep-sleep power controller. Only the
 * public nema_* API is called here; the library itself is not reconstructed. */
#include <stdint.h>

/* nema_hal.h nema_buffer_t (16 bytes, passed by value). */
typedef struct {
    int32_t size;       /* +0x0 */
    int32_t fd;         /* +0x4 */
    void *base_virt;    /* +0x8 */
    uintptr_t base_phys; /* +0xc */
} g2_nema_buffer_t;
_Static_assert(sizeof(g2_nema_buffer_t) == 16u, "stock zeroes 16 bytes");

#define G2_PWRCTRL_PERIPH_GFX 0x14u /* am_hal_pwrctrl_periph_e index of the GPU */
#define G2_GPU_MODE_HP 3u
#define G2_STENCIL_WIDTH 576
#define G2_STENCIL_HEIGHT 288

extern uint32_t audio_power_peripheral_on(uint32_t);           /* am_hal_pwrctrl_periph_enable 0x47f5b8 */
extern uint32_t audio_power_peripheral_off(uint32_t);          /* am_hal_pwrctrl_periph_disable 0x47f7ae */
extern uint32_t g2_power_gpu_mode_select(uint32_t mode);       /* am_hal_pwrctrl_gpu_mode_select 0x47f11c */
extern uint32_t am_hal_pwrctrl_gpu_mode_status_47f108(uint8_t *mode);
extern void audio_ble_hci_boot_log_4733ee(const char *, ...);  /* am_util_stdio_printf */
extern int32_t nema_init_4b10c0(void);
extern uint32_t audio_uart_nema_get_error_4b128a(void);        /* nema_get_error */
extern void audio_uart_lv_memzero_48949c(void *, uint32_t);
extern void nema_vg_init_stencil_prealloc_522400(int32_t width, int32_t height,
                                                 g2_nema_buffer_t stencil);
extern int32_t audio_uart_nema_power_control_51419a(uint32_t, uint32_t);

static const char msg_hp_failed[] = "gpu switch to HP mode failed!\n"; /* ROM 0x75d550 */
static const char msg_gfx_failed[] = "NemaGFX init failed!\n";          /* ROM 0x774ad4 */
static const char msg_vg_failed[] = "NemaVG init failed!\n";            /* ROM 0x774aec */

void gpu_nema_init_59fae0(void)
{
    uint8_t mode;
    g2_nema_buffer_t stencil;

    (void)audio_power_peripheral_off(G2_PWRCTRL_PERIPH_GFX);
    (void)g2_power_gpu_mode_select(G2_GPU_MODE_HP);
    (void)am_hal_pwrctrl_gpu_mode_status_47f108(&mode);
    if (mode != G2_GPU_MODE_HP)
        audio_ble_hci_boot_log_4733ee(msg_hp_failed);
    (void)audio_power_peripheral_on(G2_PWRCTRL_PERIPH_GFX);

    (void)nema_init_4b10c0();
    if (audio_uart_nema_get_error_4b128a() != 0u)
        audio_ble_hci_boot_log_4733ee(msg_gfx_failed);

    audio_uart_lv_memzero_48949c(&stencil, sizeof stencil);
    nema_vg_init_stencil_prealloc_522400(G2_STENCIL_WIDTH, G2_STENCIL_HEIGHT, stencil);
    if (audio_uart_nema_get_error_4b128a() != 0u)
        audio_ble_hci_boot_log_4733ee(msg_vg_failed);

    (void)audio_uart_nema_power_control_51419a(2u, 1u);
}
