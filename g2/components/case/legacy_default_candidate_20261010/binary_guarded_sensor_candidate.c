/* SPDX-License-Identifier: MIT
 * Stock 0x080035b8 recursion guard around sensor transaction.
 */
#include <stdint.h>

extern uint32_t case_binary_sensor_transaction(uint32_t selector,
                                                void *destination,
                                                uint32_t length);

uint32_t case_binary_guarded_sensor_read(uint32_t selector, void *destination,
                                         uint32_t length)
{
    volatile uint8_t *guard = (volatile uint8_t *)(uintptr_t)0x20000029u;
    if (*guard != 0u)
        return selector;
    *guard = 1u;
    case_binary_sensor_transaction(selector, destination, length);
    *guard = 0u;
    return 0u;
}
