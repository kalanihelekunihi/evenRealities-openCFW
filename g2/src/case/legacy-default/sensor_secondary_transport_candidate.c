/* SPDX-License-Identifier: MIT
 * Stock 0x0800292c secondary read and 0x08002a00 write transactions.
 * Both use the sourced serial helpers and live sensor ACK/data response.
 */
#include <stdint.h>
extern uint32_t case_binary_sensor_start(void);
extern void case_binary_sensor_byte_output(uint32_t);
extern uint32_t case_binary_sensor_ack(void);
extern uint32_t case_binary_sensor_byte_input(void);
extern void case_binary_sensor_final_pulse(void);
extern void case_binary_sensor_interbyte_pulse(void);
extern void case_binary_sensor_stop(void);
/* Stock 0x0800292C (case_serial_read_70) */
uint32_t case_legacy_ee_transport(uint32_t selector,void *response,uint32_t count)
{
    uint8_t *out=(uint8_t *)response;
    *(volatile uint8_t *)(uintptr_t)0x20000114u=0u;
    case_binary_sensor_start();
    case_binary_sensor_byte_output(0x70u);
    if(case_binary_sensor_ack()!=0u) goto failed;
    case_binary_sensor_byte_output(selector);
    if(case_binary_sensor_ack()!=0u) goto failed;
    case_binary_sensor_start();
    case_binary_sensor_byte_output(0x71u);
    if(case_binary_sensor_ack()!=0u) goto failed;
    for(uint16_t i=0;(uint32_t)i<count;i=(uint16_t)(i+1u)){
        out[i]=(uint8_t)case_binary_sensor_byte_input();
        if((uint32_t)i==count-1u)case_binary_sensor_final_pulse();
        else case_binary_sensor_interbyte_pulse();
    }
    case_binary_sensor_stop();
    return 1u;
failed:
    case_binary_sensor_stop();
    return 0u;
}
/* Stock 0x08002A00 (case_serial_write_pair_70) */
uint32_t case_legacy_pmic_transport(uint32_t selector,uint32_t value)
{
    uint8_t retries=0u;
    *(volatile uint8_t *)(uintptr_t)0x20000114u=0u;
    do{
        case_binary_sensor_start();
        case_binary_sensor_byte_output(0x70u);
        if(case_binary_sensor_ack()==0u)break;
        retries=(uint8_t)(retries+1u);
    }while(retries<200u);
    if(retries!=200u){
        case_binary_sensor_byte_output(selector);
        if(case_binary_sensor_ack()==0u){
            case_binary_sensor_byte_output(value);
            if(case_binary_sensor_ack()==0u){
                case_binary_sensor_stop();
                return 1u;
            }
        }
    }
    case_binary_sensor_stop();
    return 0u;
}
