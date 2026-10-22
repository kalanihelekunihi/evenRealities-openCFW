#include "case_logger_contract.h"
#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08007f2c periodic PMIC/battery/aging policy worker.
 */
#include <stdint.h>
extern void case_boot_periodic_power_update(void); /* 0x2a68 */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
extern void case_boot_temperature_sample(uint32_t *); /* 0x9ff0 */
extern void case_boot_current_sample(uint32_t *); /* 0x9f18 */
extern void case_boot_battery_sample(uint32_t *); /* 0xa01e */
extern void case_init_pmic_prepare(void); /* 0x9df4 */
extern uint32_t case_init_pmic_write(uint32_t,uint32_t); /* 0x39c8 */
#include "case_battery_measurement_contract.h"
extern uint32_t case_init_pmic_reset(uint32_t,uint32_t); /* 0x39e4 */
extern uint32_t case_init_pmic_read(uint32_t,uint8_t *,uint32_t); /* 0x35d4 */
extern void case_init_power_set(uint32_t); /* 0x2c8e */
extern void case_init_boost_set(uint32_t); /* 0x2c30 */
extern void case_init_wake_mask(uint32_t); /* 0x5094 */
extern void case_init_wake_config(uint32_t); /* 0x50a8 */
extern void case_init_wake_clock(void); /* 0x50c4 */
extern void case_policy_box_failure_reset(void); /* 0x12e4 */
extern void case_boot_transport_stop_clock(uint32_t); /* 0x6b80 */
extern void case_boot_aging_begin(void); /* 0x1334 */
extern void case_policy_wait(uint32_t); /* 0xa7b0 */
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void logline(uint32_t a){(void)case_policy_log(a);(void)case_policy_log(CASE_STRING_ADDR(080081c0));}
/* Stock 0x08007F2C (g2_thread_entry_2) */
void case_boot_transport_cb_7f2c(void)
{
    uint8_t stuck=0u;
    for(;;){
        case_boot_periodic_power_update();
        uint32_t ticks=rd(0x20000884u);
        if(ticks-case_policy_sensor_divide(ticks,5u)*5u==0u){
            uint32_t temperature=0u,current=0u,voltage=0u;
            case_boot_temperature_sample(&temperature);
            case_boot_current_sample(&current);
            case_boot_battery_sample(&voltage);
            if(current==123456u){
                case_init_pmic_prepare();
                (void)case_init_pmic_write(10u,0x40u);
                (void)case_init_pmic_write(11u,0xffu);
                uint32_t percent=0u;case_boot_battery_percent(&percent);
                wb(0x2000087du,(uint8_t)percent);
            }
            if(rb(0x2000087du)==99u && rb(0x2000087fu)!=0u){
                uint8_t old=stuck;stuck=(uint8_t)(stuck+1u);
                if(old>60u){stuck=0u;if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(080081a0));wb(0x2000087du,100u);}
            }else stuck=0u;
            if(rb(0x20000895u)==0u && rb(0x200000bfu)==0u){
                uint32_t format=rb(0x20000891u)!=0u?CASE_STRING_ADDR(0800d7b8):CASE_STRING_ADDR(0800d828);
                (void)case_policy_log(format,voltage,rb(0x2000087du),rb(0x20000880u),current,
                    rb(0x2000087fu),rb(0x2000088cu),rb(0x2000088du),rb(0x20000892u),
                    rb(0x200000f5u),rb(0x20000895u));
                (void)case_policy_log(CASE_STRING_ADDR(080081c0));
            }
            if(temperature<451u || rb(0x20000892u)==0u){
                if(temperature-1u<399u && rb(0x20000892u)==0u){
                    if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(080081f4));
                    (void)case_init_pmic_reset(0x16u,0u);
                    wb(0x20000892u,1u);
                }
            }else{
                if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(080081cc));
                (void)case_init_pmic_reset(0x16u,0x10u);
                wb(0x20000892u,0u);
            }
            if(rb(0x2000087du)==0u && rb(0x2000087fu)==0u){
                uint32_t battery=0u;case_boot_battery_sample(&battery);
                if(battery<3250u){
                    if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(0800822c));
                    uint8_t scratch=0u;
                    (void)case_init_pmic_read(0x10u,&scratch,1u);
                    (void)case_init_pmic_read(0x11u,&scratch,1u);
                    case_init_power_set(0u);case_init_boost_set(0u);
                    case_init_wake_mask(0x2bu);case_init_wake_config(0x2020u);
                    wr(0x40007018u,0x1003fu);case_init_wake_clock();
                }
            }
            if(rb(0x200000f4u)!=0u && rb(0x200000f5u)==0u){
                if(rb(0x2000087eu)!=4u){
                    case_policy_box_failure_reset();
                    case_boot_transport_stop_clock(1u);
                    wb(0x2000087eu,4u);
                    if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(08008254));
                }
                if(rb(0x200008aeu)<100u || rb(0x200008cau)<100u){
                    uint32_t age=rd(0x200000fcu);
                    if(age<7200u){
                        wr(0x200000fcu,age+5u);
                        if(rb(0x200000bfu)==0u){
                            (void)case_policy_log(CASE_STRING_ADDR(080082b4),rd(0x200008b2u),rb(0x200008aeu),
                                *(volatile uint16_t *)(uintptr_t)0x200008ceu,
                                rb(0x200008cau),rd(0x200000fcu));
                            (void)case_policy_log(CASE_STRING_ADDR(080081c0));
                        }
                        goto wait;
                    }
                    if(rb(0x200000bfu)==0u)logline(CASE_STRING_ADDR(08008274));
                }
                case_boot_aging_begin();
            }
        }
wait:
        case_policy_wait(1000u);
    }
}
