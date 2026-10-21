/* SPDX-License-Identifier: MIT
 * Full read transaction at fixed-image 0x080028b4.  The byte and pulse
 * operations remain typed platform contracts; no sensor values are invented.
 */
#include <stdint.h>

extern uint32_t case_binary_sensor_start(void);
extern void case_binary_sensor_byte_output(uint32_t value);
extern uint32_t case_binary_sensor_ack(void);
extern uint32_t case_binary_sensor_byte_input(void);
extern void case_binary_sensor_interbyte_pulse(void);
extern void case_binary_sensor_final_pulse(void);
extern void case_binary_sensor_stop(void);

uint32_t case_binary_sensor_transaction(uint32_t selector, void *destination,
                                         uint32_t count)
{
    uint8_t *output=(uint8_t *)destination;
    uint16_t index;
    uint16_t last=(uint16_t)(count-1u);
    *(volatile uint8_t *)(uintptr_t)0x20000114u=0;
    case_binary_sensor_start();
    case_binary_sensor_byte_output(200u);
    if(case_binary_sensor_ack()!=0u) goto failed;
    case_binary_sensor_byte_output(selector);
    if(case_binary_sensor_ack()!=0u) goto failed;
    case_binary_sensor_start();
    case_binary_sensor_byte_output(201u);
    if(case_binary_sensor_ack()!=0u) goto failed;
    index=0;
    while((uint32_t)index<count){
        output[index]=(uint8_t)case_binary_sensor_byte_input();
        if(index==last) case_binary_sensor_final_pulse();
        else case_binary_sensor_interbyte_pulse();
        index=(uint16_t)(index+1u);
    }
    case_binary_sensor_stop();
    return 1u;
failed:
    case_binary_sensor_stop();
    return 0u;
}
