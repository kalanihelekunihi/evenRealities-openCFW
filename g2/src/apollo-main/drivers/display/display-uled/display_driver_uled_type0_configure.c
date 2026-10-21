/* Apollo S200 JBD4010 configure command sequence at 0x5927ca. */
#include <stdint.h>

extern uint32_t display_driver_uled_type0_context_46bfe8(void);
extern void display_driver_uled_type0_context_snapshot_46c410(uint32_t,
                                                                uint32_t *,uint32_t *);
extern uint32_t display_driver_uled_command_5926ee(uint32_t,const void *,uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);
extern uint32_t display_driver_uled_delay_449376(uint32_t);
extern uint32_t display_driver_uled_type0_frame_start_5931c0(void);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern uint32_t display_driver_uled_type0_set_offset_592aa8(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type0_step_5927ca(void) {
    uint32_t brightness=0u,luminance=0u;
    display_driver_uled_type0_context_snapshot_46c410(
        display_driver_uled_type0_context_46bfe8(),&brightness,&luminance);
    uint32_t empty=0u;
    (void)display_driver_uled_command_5926ee(0x66u,&empty,0u);
    audio_ble_hci_radio_reset_4910f4(1u);
    (void)display_driver_uled_command_5926ee(0x99u,&empty,0u);
    (void)display_driver_uled_delay_449376(50u);
    (void)display_driver_uled_command_5926ee(0x06u,&empty,0u);
    uint8_t command_data[10]={0};
    command_data[0]=0x10u;
    (void)display_driver_uled_command_5926ee(0x01u,command_data,1u);
    (void)display_driver_uled_type0_frame_start_5931c0();
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(3u,(const char *)(uintptr_t)0x785c90u,
            (const char *)(uintptr_t)0x6f313cu,
            (const char *)(uintptr_t)0x753c78u,0x114u,
            (const char *)(uintptr_t)0x75f7f0u,12u,10u);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x0c800000u,
            (const char *)(uintptr_t)0x7336a4u,
            (const char *)(uintptr_t)0x7336a4u,12u,10u);
    const uint8_t clear_positions[5][2]={{0u,0u},{0u,20u},
        {24u,0u},{24u,20u},{12u,10u}};
    for (uint32_t i=0;i<5u;i++) {
        uint8_t position[2]={clear_positions[i][0],clear_positions[i][1]};
        (void)display_driver_uled_command_5926ee(0xc0u,position,2u);
        (void)display_driver_uled_command_5926ee(0x97u,&empty,0u);
        audio_ble_hci_radio_reset_4910f4(1u);
    }
    for (uint32_t i=0;i<2u;i++) {
        (void)display_driver_uled_command_5926ee(0x73u,&empty,0u);
        audio_ble_hci_boot_delay_491102(100u);
        (void)display_driver_uled_command_5926ee(0x97u,&empty,0u);
        audio_ble_hci_radio_reset_4910f4(1u);
    }
    uint32_t luminance_high=luminance>>8;
    (void)display_driver_uled_command_5926ee(0x36u,&luminance_high,2u);
    uint8_t level=(uint8_t)brightness;
    (void)display_driver_uled_command_5926ee(0x46u,&level,1u);
    uint8_t four=4u;
    (void)display_driver_uled_command_5926ee(0x31u,&four,1u);
    (void)display_driver_uled_command_5926ee(0xa3u,&empty,0u);
    (void)display_driver_uled_command_5926ee(0x97u,&empty,0u);
    audio_ble_hci_radio_reset_4910f4(1u);
    const volatile uint8_t *settings=(const volatile uint8_t *)(uintptr_t)0x20003994u;
    (void)display_driver_uled_type0_set_offset_592aa8(settings[0x2cu],
                                                         settings[0x2du]);
    return 0u;
}
