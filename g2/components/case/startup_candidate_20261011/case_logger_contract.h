/* SPDX-License-Identifier: MIT
 * Native CASE0x9170 aliases. Naked general alias preserves AAPCS word stream;
 * numbered adapters have the explicitly modeled fixed argument counts.
 */
#ifndef CASE_LOGGER_CONTRACT_H
#define CASE_LOGGER_CONTRACT_H
#include <stdint.h>
uint32_t case_policy_log(uint32_t format,...);
uint32_t case_policy_log_number(uint32_t format,uint32_t value);
uint32_t case_policy_log_four(uint32_t format,uint32_t a,uint32_t b,uint32_t c,uint32_t d);
#endif
