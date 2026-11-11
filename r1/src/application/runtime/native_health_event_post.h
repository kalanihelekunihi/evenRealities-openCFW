#ifndef R1_NATIVE_HEALTH_EVENT_POST_H
#define R1_NATIVE_HEALTH_EVENT_POST_H
#include <stdint.h>
extern volatile uint32_t r1_sync_block_field;
uint32_t r1_sync_block_field_get(void);
#define R1_EVENT_POST(name) uint32_t name(const volatile uint8_t *,uint32_t,uint32_t,uint32_t,uint32_t,volatile uint8_t *)
R1_EVENT_POST(r1_event_post_module1);
R1_EVENT_POST(r1_event_post_module2);
R1_EVENT_POST(r1_event_post_module4);
R1_EVENT_POST(r1_event_post_module5);
R1_EVENT_POST(r1_event_post_module6);
#undef R1_EVENT_POST
uint32_t r1_event_post_0x601(const volatile uint8_t *,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_ack_record_register_typed(uint32_t,uint32_t,uint32_t,volatile uint8_t *,volatile uint16_t *);
uint32_t r1_ack_record_remove_type2(uint32_t,uint32_t);
uint32_t r1_protocol_payload_copy_send(uint32_t,uint32_t,uint32_t,uint32_t,const volatile uint8_t *,uint32_t,uint32_t);
uint32_t r1_protocol_health_sample_send(uint32_t,uint32_t,uint32_t,uint32_t,const volatile uint8_t *,uint32_t);
uint32_t r1_health_get_hr_encode(const volatile uint8_t *,uint32_t,uint32_t);
uint32_t r1_health_get_hrv_encode(const volatile uint8_t *,uint32_t,uint32_t);
uint32_t r1_health_get_spo2_encode(const volatile uint8_t *,uint32_t,uint32_t);
#endif
