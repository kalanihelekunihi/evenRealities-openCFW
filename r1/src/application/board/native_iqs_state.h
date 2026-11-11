#ifndef R1_NATIVE_IQS_STATE_H
#define R1_NATIVE_IQS_STATE_H
#include <stdint.h>
/* Narrow fields in native context 0x2000772c. Existing slider flag at +4
 * and callback word at +8 retain their earlier owners. */
extern volatile uint8_t r1_iqs_control0,r1_iqs_control1;
extern volatile uint8_t r1_iqs_recovery_consecutive,r1_iqs_recovery_used;
extern volatile int8_t r1_iqs_raw_report_selection;
extern volatile uint16_t r1_iqs_last_position;
extern volatile uint16_t r1_iqs_status_live[3],r1_iqs_status_snapshot[3];
extern volatile uint32_t r1_touch_slider_callback_word;
extern const uint8_t *volatile r1_iqs_model_configuration;
extern volatile uint32_t r1_iqs_ati_error_sequence,r1_iqs_ati_last_report_tick;
void r1_iqs7211e_ati_error_audit_policy(void);
typedef void (*r1_iqs_slider_callback)(uint32_t,uint32_t,uint32_t,uint32_t,float);
extern volatile uint8_t r1_touch_slider_flag;
void r1_iqs7211e_ati_recovery_policy(void);
void r1_iqs7211e_reset_reconfigure(void);
float r1_touch_channel_average(const void *data);
void r1_touch_irq_event_dispatch(float average);
#endif
