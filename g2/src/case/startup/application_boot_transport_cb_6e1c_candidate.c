#include "case_logger_contract.h"
#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08006e1c transport event worker: startup signals and full
 * event-service loop. Child services retain independent source contracts.
 */
#include <stdint.h>
extern int32_t case_policy_event_signal(uint32_t,uint32_t); /* 0xaaf0 */
extern uint32_t case_policy_event_peek(uint32_t); /* 0xa816 */
extern int32_t case_policy_event_clear(uint32_t,uint32_t); /* 0xa7d2 */
extern void case_boot_transport_stop_link(uint32_t); /* 0x6b98 */
extern void case_boot_transport_stop_clock(uint32_t); /* 0x6b80 */
extern void log_hex_buffer(const uint8_t *,uint32_t); /* 0x67c8 */
extern uint32_t case_policy_send_probe(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x258c */
extern uint32_t case_policy_ota_transmit(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x2744 */
extern uint32_t case_policy_parse_probe(uint32_t); /* 0x1e94 */
extern uint32_t case_boot_transport_rx_restart(void); /* 0x3b90 */
extern void case_policy_no_reply_reset(uint32_t,uint32_t); /* 0x9a9c */
extern void case_init_display_reset(void); /* 0x502c */
extern void case_boot_transport_event_085c(void); /* 0x085c */
extern void case_boot_transport_left_aging(uint32_t); /* 0x23f4 */
extern void case_boot_transport_right_aging(uint32_t); /* 0x24c0 */
extern void case_policy_box_failure_reset(void); /* 0x12e4 */
extern int32_t case_policy_task_reset(uint32_t); /* 0xab26 */
extern uint32_t case_policy_service_idle(void); /* 0xd154 */
extern int32_t case_boot_sensor_finish_signal(uint32_t,uint32_t); /* 0xa888 */
extern void case_policy_wait(uint32_t); /* 0xa7b0 */
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void logline(uint32_t a){(void)case_policy_log(a);(void)case_policy_log(CASE_STRING_ADDR(0800715c));}
static uint32_t gls_ready(uint32_t side)
{
    if(side==0u)return rb(0x2000088cu)!=0u;
    return rb(0x2000088du)!=0u;
}
static void packet_send(uint32_t count)
{
    uint32_t side=rb(0x200001b6u)==0u;
    const uint8_t *packet=(const uint8_t *)(uintptr_t)0x200001b4u;
    if(rb(0x20000895u)==0u || rb(0x20000896u)==0u)
        (void)case_policy_send_probe(side,packet,count,1u);
    else (void)case_policy_ota_transmit(side,packet,count,1u);
}
void case_boot_transport_cb_6e1c(void)
{
    (void)case_policy_event_signal(rd(0x200000c8u),3000u);
    (void)case_policy_event_signal(rd(0x200000dcu),1000u);
    for(;;){
        uint32_t event=rd(0x200000f0u);
        uint32_t bits=case_policy_event_peek(event);
        if((bits&2u)!=0u){
            (void)case_policy_event_clear(event,2u);
            (void)case_policy_event_signal(rd(0x200000c8u),3000u);
        }
        if((bits&0x1000u)!=0u){(void)case_policy_event_clear(event,0x1000u);wb(0x20000893u,0u);}
        if((bits&4u)!=0u){
            (void)case_policy_event_clear(event,4u);
            wb(0x200000c4u,1u);
            case_boot_transport_stop_link(0u);
            case_boot_transport_stop_clock(rb(0x200000c4u));
            (void)case_policy_event_signal(rd(0x200000d0u),800u);
        }
        if((bits&8u)!=0u){
            (void)case_policy_event_clear(event,8u);
            case_boot_transport_event_085c();
            *(volatile uint16_t *)(uintptr_t)0x2000010au=0u;
        }
        if((bits&0x20u)!=0u && rb(0x200000bcu)==0u &&
           gls_ready(rb(0x200001b6u)!=0u)!=0u){
            (void)case_policy_event_clear(event,0x20u);
            if(rb(0x20000895u)==0u)log_hex_buffer((const uint8_t *)(uintptr_t)0x200001b4u,rb(0x200001b7u)+5u);
            wb(0x200000bcu,1u);
            packet_send(rb(0x200001b7u)+5u);
            wb(0x200000bcu,0u);
            (void)case_policy_parse_probe(1u);
        }
        if((bits&0x400u)!=0u && rb(0x200000bcu)==0u &&
           gls_ready(rb(0x200001b6u)!=0u)!=0u){
            (void)case_policy_event_clear(event,0x400u);
            wb(0x200000bcu,1u);
            packet_send((uint32_t)rb(0x200001b7u)+((uint32_t)rb(0x200001b8u)<<8)+6u);
            wb(0x200000bcu,0u);
            (void)case_policy_parse_probe(1u);
        }
        if((bits&0x40u)!=0u && case_boot_transport_rx_restart()!=0u){
            if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(08007148));
            (void)case_policy_event_clear(event,0x40u);
        }
        if((bits&0x100u)!=0u){
            if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(08007160));
            case_policy_no_reply_reset(1u,1u);
            (void)case_policy_event_clear(event,0x100u);
        }
        if((bits&0x200u)!=0u){
            if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(08007180));
            case_policy_no_reply_reset(1u,1u);
            (void)case_policy_event_clear(event,0x200u);
            case_init_display_reset();
        }
        if((bits&0x80u)!=0u){
            wb(0x200000f4u,0u);wr(0x200000fcu,0u);
            wb(0x200000f5u,0u);wb(0x200000fau,0u);
            if(gls_ready(0u)!=0u && rb(0x200000f6u)!=0u){
                uint32_t i=0u;while(i<10u && rb(0x200000f6u)!=0u){case_boot_transport_left_aging(0u);++i;}
                if(i<10u && rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(08007194));
                case_policy_wait(50u);
            }
            if(gls_ready(1u)!=0u && rb(0x200000f7u)!=0u){
                uint32_t i=0u;while(i<10u && rb(0x200000f7u)!=0u){case_boot_transport_right_aging(0u);++i;}
                if(i<10u && rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(080071b4));
                case_policy_wait(50u);
            }
            if((rb(0x200000f6u)!=0u || rb(0x200000f7u)!=0u) && rb(0x200000bfu)==0u){
                (void)case_policy_log(CASE_STRING_ADDR(080071d4),rb(0x200000f6u),rb(0x200000f7u));
                (void)case_policy_log(CASE_STRING_ADDR(0800715c));
            }
            case_policy_box_failure_reset();
            (void)case_policy_task_reset(rd(0x200000d4u));
            (void)case_policy_task_reset(rd(0x200000d8u));
            (void)case_policy_event_clear(event,0x80u);
            wb(0x20000891u,1u);
            (void)case_policy_service_idle();
            wb(0x2000088cu,0u);wb(0x2000088du,0u);
        }
        if(rb(0x200000bdu)!=0u){
            (void)case_boot_sensor_finish_signal(event,0x20u);
            wb(0x200001b4u,0x24u);wb(0x200001b5u,0u);
            wb(0x200001b6u,1u);wb(0x200001b7u,0u);wb(0x200001b8u,0xa7u);
        }
        case_policy_wait(1u);
    }
}
