/* Apollo S200 JBD4010 brightness command sequence at 0x592e9c. */
#include <stdint.h>

extern uint32_t display_driver_uled_mode_45a568(void);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);
extern void display_driver_uled_command_5926ee(uint32_t,const void *,uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);

void display_driver_uled_type0_aux_config_592e9c(uint32_t first,
                                                   uint32_t second,
                                                   uint32_t third) {
    uint32_t mode=display_driver_uled_mode_45a568() & 255u;
    const char *kind=(const char *)(uintptr_t)(mode==1u ? 0x593080u :
                              mode==2u ? 0x593084u : 0x593088u);
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(3u,(const char *)(uintptr_t)0x785c90u,
            (const char *)(uintptr_t)0x6f313cu,
            (const char *)(uintptr_t)0x74986cu,0x23cu,
            (const char *)(uintptr_t)0x728f74u,kind,first,second,third);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x0d000000u,
            (const char *)(uintptr_t)0x70247cu,
            (const char *)(uintptr_t)0x70247cu,kind,first,second,third);

    uint8_t payload[20]={0};
    display_driver_uled_command_5926ee(6u,payload,0u);
    display_driver_uled_command_5926ee(0xa9u,payload,0u);
    uint32_t high=(uint32_t)((int32_t)second >> 8);
    uint8_t pair[8];
    pair[0]=(uint8_t)high;pair[1]=(uint8_t)(high>>8);
    pair[2]=(uint8_t)(high>>16);pair[3]=(uint8_t)(high>>24);
    pair[4]=(uint8_t)second;pair[5]=(uint8_t)(second>>8);
    pair[6]=(uint8_t)(second>>16);pair[7]=(uint8_t)(second>>24);
    display_driver_uled_command_5926ee(0x36u,pair,2u);
    display_driver_uled_command_5926ee(0x46u,&third,1u);
    uint32_t four=4u;
    display_driver_uled_command_5926ee(0x31u,&four,1u);
    display_driver_uled_command_5926ee(0xa3u,&four,0u);
    display_driver_uled_command_5926ee(0x97u,&four,0u);
    audio_ble_hci_radio_reset_4910f4(1u);
}
