/* SPDX-License-Identifier: MIT
 * Stock CASE GPIO leaf ABI: 0x08004e9e/0x08006b80/0x08006b98.
 * All selected product callers discard R0; register writes use a normalized
 * nonzero enable. Separate source wrapper addresses remain distinct.
 */
#ifndef CASE_GPIO_CONTROL_CONTRACT_H
#define CASE_GPIO_CONTROL_CONTRACT_H
#include <stdint.h>
void case_control_write(uint32_t base,uint32_t mask,uint32_t enable);
void case_control_a(uint32_t enable);
void case_control_b(uint32_t enable);
#endif
