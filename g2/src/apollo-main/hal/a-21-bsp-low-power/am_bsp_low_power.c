/* Board support (AmbiqSuite apollo510 am_bsp.c shape, product build; the BSP
 * is not in the pinned upstream HAL). Native 0x4c2ae8..0x4c2b68:
 * am_bsp_low_power_init 0x4c2ae8, am_bsp_itm_printf_disable 0x4c2b30;
 * literal pool words 0x4c306c/0x4c3070/0x4c3200.
 *
 * Low-power init discards every status. Board info handed to the clock
 * manager (ROM 0x77d8f8): XTAL-HS mode 0 / 0 Hz, XTAL-LS 32768 Hz, external
 * reference 12 MHz. HFRC and HFRC2 are then set to free-run (0 Hz request).
 * Uses a hard-float call (temperature update at 25.0 C): profile
 * g2-apollo-main-3. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t xtal_hs_mode;  /* +0x00 */
    uint8_t pad[3];
    uint32_t xtal_hs_hz;   /* +0x04 */
    uint32_t reserved_08;  /* +0x08 */
    uint32_t xtal_ls_hz;   /* +0x0c */
    uint32_t ext_ref_hz;   /* +0x10 */
} g2_clkmgr_board_info_t;
_Static_assert(sizeof(g2_clkmgr_board_info_t) == 20u, "stock board info copy is 20 bytes");

typedef struct {
    float low_threshold;  /* +0 */
    float high_threshold; /* +4 */
} g2_pwrctrl_temp_thresh_t;
_Static_assert(sizeof(g2_pwrctrl_temp_thresh_t) == 8u, "am_hal_pwrctrl_temp_thresh_t");

extern volatile uint8_t g2_bsp_itm_print_enabled;                 /* RAM 0x20074f4e */
extern const uint32_t g2_gpio_pincfg_default;                     /* ROM 0x78ee3c (am_hal_gpio_pincfg_default) */
extern const g2_clkmgr_board_info_t g2_clkmgr_board_info_default; /* ROM 0x77d8f8 */

extern uint32_t am_hal_itm_disable_539254(void);
extern uint32_t am_hal_tpiu_disable(void); /* Stock 0x539304, reference-counted TPIU power-down */
extern void log_output_hook_set_472c7c(void (*hook)(const char *text)); /* am_util_stdio_printf_init */
extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern uint32_t am_hal_pwrctrl_low_power_init_47fae8(void);
extern uint32_t am_hal_pwrctrl_control_47fea0(uint32_t control, void *args);
extern __attribute__((pcs("aapcs-vfp")))
uint32_t am_hal_pwrctrl_temp_update_480028(float temperature_c, g2_pwrctrl_temp_thresh_t *thresholds);
extern void audio_uart_checksum_copy(void *destination, const void *source, uint32_t length); /* 0x439c04 */
extern uint32_t audio_clock_board_set(const void *info); /* 0x4c45e2 am_hal_clkmgr_board_info_set */
extern uint32_t audio_clock_config(uint32_t clock, uint32_t hz, const uint32_t *config); /* 0x4c446c am_hal_clkmgr_clock_config */

#define BSP_GPIO_ITM_SWO 28u
#define CLKMGR_CLK_ID_HFRC 4u
#define CLKMGR_CLK_ID_HFRC2 5u

void am_bsp_itm_printf_disable_4c2b30(void)
{
    if (g2_bsp_itm_print_enabled != 1u)
        return;
    if (am_hal_itm_disable_539254() != 0u)
        for (;;) {
        }
    if (am_hal_tpiu_disable() != 0u)
        for (;;) {
        }
    log_output_hook_set_472c7c(NULL);
    (void)am_hal_gpio_pinconfig_480f0c(BSP_GPIO_ITM_SWO, g2_gpio_pincfg_default);
    g2_bsp_itm_print_enabled = 0u;
}

void am_bsp_low_power_init_4c2ae8(void)
{
    g2_pwrctrl_temp_thresh_t thresholds;
    g2_clkmgr_board_info_t board;
    am_bsp_itm_printf_disable_4c2b30();
    (void)am_hal_pwrctrl_low_power_init_47fae8();
    (void)am_hal_pwrctrl_control_47fea0(0u, NULL);
    (void)am_hal_pwrctrl_temp_update_480028(25.0f, &thresholds);
    audio_uart_checksum_copy(&board, &g2_clkmgr_board_info_default, sizeof(board));
    (void)audio_clock_board_set(&board);
    (void)audio_clock_config(CLKMGR_CLK_ID_HFRC, 0u, NULL);
    (void)audio_clock_config(CLKMGR_CLK_ID_HFRC2, 0u, NULL);
}
