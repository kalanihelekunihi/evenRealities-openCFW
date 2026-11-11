/* Apollo S200 JBD4010 display offset at 0x592aa8. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_nvdb_legacy_psn_flag[] __asm__("g2_nvdb_legacy_psn_flag");

extern uint32_t display_driver_uled_mode_45a568(void);
extern uint32_t display_driver_uled_command_5926ee(uint32_t,const void *,uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static void log_failure(uint32_t line,uint32_t detail,uint32_t short_detail) {
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(1u,"driver.jbd4010" /* stock 0x785c90 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c" /* stock 0x6f313c */,
            "am_devices_jbd4010_set_display_offset" /* stock 0x74981c */,line,
            (const char *)(uintptr_t)detail);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x04000000u,
            (const char *)(uintptr_t)short_detail,
            (const char *)(uintptr_t)short_detail);
}

uint32_t display_driver_uled_type0_set_offset_592aa8(uint32_t horizontal,
                                                       uint32_t vertical) {
    uint8_t x=(uint8_t)horizontal,y=(uint8_t)vertical;
    if (*(volatile const uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_nvdb_legacy_psn_flag)!=0u &&
        display_driver_uled_mode_45a568()==2u)
        x=(uint8_t)(x+5u);
    if (x<2u) x=2u;
    if (x>22u) x=22u;
    if (y<2u) y=2u;
    if (y>18u) y=18u;
    uint32_t empty=0u;
    if (display_driver_uled_command_5926ee(0xa9u,&empty,0u)!=0u) {
        log_failure(0x175u,(uint32_t)(uintptr_t)"Failed to disable display" /* stock 0x76b19c */,(uint32_t)(uintptr_t)"[driver.jbd4010]Failed to disable display" /* stock 0x73e47c */);
        return UINT32_MAX;
    }
    uint8_t position[2]={x,y};
    if (display_driver_uled_command_5926ee(0xc0u,position,2u)!=0u) {
        log_failure(0x17eu,(uint32_t)(uintptr_t)"Failed to write offset register" /* stock 0x75f810 */,(uint32_t)(uintptr_t)"[driver.jbd4010]Failed to write offset register" /* stock 0x7336d4 */);
        return UINT32_MAX;
    }
    if (display_driver_uled_command_5926ee(0xa3u,&empty,0u)!=0u) {
        log_failure(0x185u,(uint32_t)(uintptr_t)"Failed to enable display" /* stock 0x76b1b8 */,(uint32_t)(uintptr_t)"[driver.jbd4010]Failed to enable display" /* stock 0x73e4a8 */);
        return UINT32_MAX;
    }
    (void)display_driver_uled_command_5926ee(0x97u,&empty,0u);
    audio_ble_hci_radio_reset_4910f4(1u);
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(3u,"driver.jbd4010" /* stock 0x785c90 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c" /* stock 0x6f313c */,
            "am_devices_jbd4010_set_display_offset" /* stock 0x74981c */,0x18cu,
            "Display offset set successfully: x=%d, y=%d" /* stock 0x73e4d4 */,x,y);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x0c800000u,
            "[driver.jbd4010]Display offset set successfully: x=%d, y=%d" /* stock 0x7147c4 */,
            "[driver.jbd4010]Display offset set successfully: x=%d, y=%d" /* stock 0x7147c4 */,x,y);
    return 0u;
}
