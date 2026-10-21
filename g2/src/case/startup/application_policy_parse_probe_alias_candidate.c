/* SPDX-License-Identifier: MIT
 * Native 0x1e94 parser already sourced as record dispatcher.
 */
#include <stdint.h>
extern uint32_t case_record_dispatch_1e94(uint32_t side);
uint32_t case_policy_parse_probe(uint32_t side)
{return case_record_dispatch_1e94(side);}
