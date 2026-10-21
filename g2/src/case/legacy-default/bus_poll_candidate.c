/* SPDX-License-Identifier: MIT
 * Stock 0x0800c43c response wrapper. The 0x0800b53c timed GPIO
 * sampling loop remains a typed live-device contract.
 */
#include <stdint.h>
extern uint32_t case_bus_response_sample(uint32_t *word);
uint32_t case_bus_poll(uint32_t *word)
{
    uint32_t sample=0u;
    uint32_t result=case_bus_response_sample(&sample);
    *word=sample;
    return result;
}
