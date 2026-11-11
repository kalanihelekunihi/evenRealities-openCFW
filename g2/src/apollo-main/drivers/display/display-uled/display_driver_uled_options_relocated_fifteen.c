/* Partial source-owned S200 uLED option records. Fifteen callbacks use C symbols;
 * the other 14 distinct callback addresses remain authenticated native values.
 */
#include <stdint.h>
extern void display_driver_uled_option_type0_irq_592658(void);
extern void display_driver_uled_option_type1_irq_5bbd48(void);
extern uint32_t display_driver_uled_option_type1_mask_5bcc10(uint32_t);
extern uint32_t display_driver_uled_option_type1_noop_5bd39c(void);
extern uint32_t display_driver_uled_option_type0_setup_592680(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_option_type1_setup_5bbd70(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_option_type0_enable_5926b4(uint32_t);
extern uint32_t display_driver_uled_option_type1_enable_5bbda4(uint32_t);
extern uint32_t display_driver_uled_type1_pre_5bcb6c(void);
extern uint32_t display_driver_uled_type0_pre_593200(void);
extern uint32_t display_driver_uled_type0_frame_start_5931c0(void);
extern uint32_t display_driver_uled_type1_frame_start_5bcb28(void);
extern uint32_t display_driver_uled_type1_finish_5bcbb4(void);
extern uint32_t display_driver_uled_type0_finish_59328c(void);
extern uint32_t display_driver_uled_type0_aux_finish_5936a4(void);

/* sim15: the remaining raw stock Thumb addresses in these two option tables
 * are mapped to our implementations. Evidence: g2/symbols/apollo_main.tsv
 * names each stock entry (e.g. 0x592f9a am_devices_mspi_jbd4010_read_chipId,
 * 0x5bcc18 am_devices_hongshi_QSPI_PartialReflash) and our symbol carries the
 * same stock address suffix or the same stock name. Raw values jumped into
 * unrelated code in our image. */
extern const unsigned char g2ref_display_driver_uled_type1_get_5bc76e[] __asm__("display_driver_uled_type1_get_5bc76e"); /* stock 0x5bc76e */
extern const unsigned char g2ref_display_driver_uled_type1_set_brightness_5bc6ae[] __asm__("display_driver_uled_type1_set_brightness_5bc6ae"); /* stock 0x5bc6ae */
extern const unsigned char g2ref_display_driver_uled_type1_set_offset_5bc4c0[] __asm__("display_driver_uled_type1_set_offset_5bc4c0"); /* stock 0x5bc4c0 */
extern const unsigned char g2ref_display_driver_uled_type1_frame_lower_5bcd44[] __asm__("display_driver_uled_type1_frame_lower_5bcd44"); /* stock 0x5bcd44 */
extern const unsigned char g2ref_am_devices_hongshi_QSPI_PartialReflash[] __asm__("am_devices_hongshi_QSPI_PartialReflash"); /* stock 0x5bcc18 */
extern const unsigned char g2ref_am_devices_hongshi_status_check_and_recovery[] __asm__("am_devices_hongshi_status_check_and_recovery"); /* stock 0x5bd014 */
extern const unsigned char g2ref_display_driver_uled_type1_read_sn_5bc8b4[] __asm__("display_driver_uled_type1_read_sn_5bc8b4"); /* stock 0x5bc8b4 */
extern const unsigned char g2ref_display_driver_uled_type0_get_592f9a[] __asm__("display_driver_uled_type0_get_592f9a"); /* stock 0x592f9a */
extern const unsigned char g2ref_display_driver_uled_type0_aux_config_592e9c[] __asm__("display_driver_uled_type0_aux_config_592e9c"); /* stock 0x592e9c */
extern const unsigned char g2ref_jbd4010_set_current_6bit[] __asm__("jbd4010_set_current_6bit"); /* stock 0x593334 */
extern const unsigned char g2ref_display_driver_uled_type0_set_offset_592aa8[] __asm__("display_driver_uled_type0_set_offset_592aa8"); /* stock 0x592aa8 */
extern const unsigned char g2ref_display_driver_uled_type0_frame_lower_592dea[] __asm__("display_driver_uled_type0_frame_lower_592dea"); /* stock 0x592dea */
extern const unsigned char g2ref_am_devices_jbd4010_QSPI_PartialReflash[] __asm__("am_devices_jbd4010_QSPI_PartialReflash"); /* stock 0x592cb4 */
extern const unsigned char g2ref_am_devices_jbd4010_set_mode[] __asm__("am_devices_jbd4010_set_mode"); /* stock 0x593750 */

const uintptr_t display_driver_uled_option_type1[16] = {
    (uintptr_t)&display_driver_uled_option_type1_irq_5bbd48,
    (uintptr_t)g2ref_display_driver_uled_type1_get_5bc76e,
    (uintptr_t)&display_driver_uled_option_type1_setup_5bbd70,
    (uintptr_t)&display_driver_uled_option_type1_enable_5bbda4,
    (uintptr_t)&display_driver_uled_type1_pre_5bcb6c, (uintptr_t)&display_driver_uled_type1_finish_5bcbb4, (uintptr_t)g2ref_display_driver_uled_type1_set_brightness_5bc6ae, (uintptr_t)&display_driver_uled_type1_frame_start_5bcb28,
    (uintptr_t)&display_driver_uled_option_type1_mask_5bcc10,
    (uintptr_t)g2ref_display_driver_uled_type1_set_offset_5bc4c0, (uintptr_t)g2ref_display_driver_uled_type1_frame_lower_5bcd44, (uintptr_t)g2ref_am_devices_hongshi_QSPI_PartialReflash,
    (uintptr_t)g2ref_am_devices_hongshi_status_check_and_recovery,
    (uintptr_t)&display_driver_uled_option_type1_noop_5bd39c,
    (uintptr_t)g2ref_display_driver_uled_type1_read_sn_5bc8b4, 0x00000001u
};

const uintptr_t display_driver_uled_option_type0[16] = {
    (uintptr_t)&display_driver_uled_option_type0_irq_592658,
    (uintptr_t)g2ref_display_driver_uled_type0_get_592f9a,
    (uintptr_t)&display_driver_uled_option_type0_setup_592680,
    (uintptr_t)&display_driver_uled_option_type0_enable_5926b4,
    (uintptr_t)&display_driver_uled_type0_pre_593200, (uintptr_t)&display_driver_uled_type0_finish_59328c, (uintptr_t)g2ref_display_driver_uled_type0_aux_config_592e9c, (uintptr_t)&display_driver_uled_type0_frame_start_5931c0,
    (uintptr_t)g2ref_jbd4010_set_current_6bit, (uintptr_t)g2ref_display_driver_uled_type0_set_offset_592aa8, (uintptr_t)g2ref_display_driver_uled_type0_frame_lower_592dea, (uintptr_t)g2ref_am_devices_jbd4010_QSPI_PartialReflash,
    (uintptr_t)&display_driver_uled_type0_aux_finish_5936a4, (uintptr_t)g2ref_am_devices_jbd4010_set_mode, 0x00000000u, 0x00000000u
};

_Static_assert(sizeof display_driver_uled_option_type1 == 64u, "uLED option size");
_Static_assert(sizeof display_driver_uled_option_type0 == 64u, "uLED option size");
