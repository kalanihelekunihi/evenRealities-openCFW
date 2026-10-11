/* SPDX-License-Identifier: MIT
 * Exact native entry aliases 0x9004, 0x9040, 0xd218, 0x9170.
 */
#include <stdint.h>
extern uint32_t case_watchdog_frame_pack(uint32_t reg,uint32_t count,const uint8_t *bytes); /* 0x9004 */
extern uint32_t case_legacy_aa_read(uint32_t reg,uint32_t count,void *out); /* 0x9040 */
extern uint32_t case_legacy_aa_second(uint32_t prior); /* 0xd218 */
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
uint32_t case_init_secondary_write(uint32_t reg,uint32_t count,const uint8_t *bytes)
{return case_watchdog_frame_pack(reg,count,bytes);}
uint32_t case_init_secondary_read(uint32_t reg,uint32_t count,uint8_t *out)
{return case_legacy_aa_read(reg,count,out);}
uint32_t case_init_service_ready(void)
{return case_legacy_aa_second(0u);}
uint32_t case_init_log(uint32_t format,uint32_t arg0,uint32_t arg1,uint32_t arg2)
{return case_legacy_logger((const char *)(uintptr_t)format,arg0,arg1,arg2);}
