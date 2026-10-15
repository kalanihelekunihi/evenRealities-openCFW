/* Apollo S200 type-0 auxiliary recovery sequence at 0x593528. */
#include <stdint.h>

extern uint32_t display_driver_uled_type0_context_46bfe8(void);
extern void display_driver_uled_type0_context_snapshot_46c410(uint32_t,
                                                                uint32_t *,uint32_t *);
extern uint32_t display_driver_uled_type0_finish_59328c(void);
extern uint32_t display_driver_uled_type0_pre_593200(void);
extern void display_driver_uled_type0_step_5927ca(void);
extern uint32_t display_driver_uled_type0_frame_lower_592dea(uint32_t,uint32_t,
    uint32_t,uint32_t,uint32_t,uint32_t);
extern void display_driver_uled_type0_aux_config_592e9c(uint32_t,uint32_t,
                                                          uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static void stage_log(uint32_t line,const char *detail,const char *short_detail) {
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(3u,(const char *)(uintptr_t)0x785c90u,
            (const char *)(uintptr_t)0x6f313cu,
            (const char *)(uintptr_t)0x776d3cu,line,detail);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x0c000000u,short_detail,short_detail);
}

void display_driver_uled_type0_aux_recover_593528(void) {
    uint32_t saved_a=0u,saved_b=0u;
    uint32_t context=display_driver_uled_type0_context_46bfe8();
    display_driver_uled_type0_context_snapshot_46c410(context,&saved_a,&saved_b);
    (void)display_driver_uled_type0_finish_59328c();
    stage_log(0x310u,(const char *)(uintptr_t)0x776d54u,
              (const char *)(uintptr_t)0x7498e4u);
    audio_ble_hci_radio_reset_4910f4(1u);
    (void)display_driver_uled_type0_pre_593200();
    stage_log(0x314u,(const char *)(uintptr_t)0x776d6cu,
              (const char *)(uintptr_t)0x74990cu);
    display_driver_uled_type0_step_5927ca();
    stage_log(0x316u,(const char *)(uintptr_t)0x776d84u,
              (const char *)(uintptr_t)0x749934u);
    audio_ble_hci_radio_reset_4910f4(1u);
    (void)display_driver_uled_type0_frame_lower_592dea(0u,0u,0u,0u,
                                                         0x280u,0x1e0u);
    audio_ble_hci_radio_reset_4910f4(1u);
    display_driver_uled_type0_aux_config_592e9c(0u,saved_b,saved_a);
}
