/* SPDX-License-Identifier: MIT
 * Adapters from the logger-facing helper names to the selected bounded Main
 * libc-style helpers (memset 0x43c0e4, strlen 0x44a43c, strstr 0x44b63a,
 * snprintf "%ld" 0x44b728). The EasyLogger adapters that used to live here
 * (output lock/unlock, tag-level policy, format masks, elog_strcpy, leveled
 * port output) are now the upstream EasyLogger elog.c / elog_utils.c units
 * and the port in system/a-03-elog-async/elog_port_output.c.
 */
#include <stdbool.h>
#include <stdint.h>

extern uint32_t g2_log_candidate_module_length(const uint8_t *);
extern uint32_t g2_log_candidate_find_token(const uint8_t *,const uint8_t *);
extern uint32_t g2_log_candidate_timestamp_5(uint8_t *,uint32_t);
extern void g2_log_candidate_stack_fill(uint8_t *,uint32_t,uint32_t);

void g2_log_stack_fill(char *destination,uint32_t count,uint8_t value)
{
    g2_log_candidate_stack_fill((uint8_t *)destination,count,value);
}

uint32_t g2_log_module_length(const char *module)
{
    return g2_log_candidate_module_length((const uint8_t *)module);
}
int32_t g2_log_contains(const char *text,const char *token)
{
    return (int32_t)g2_log_candidate_find_token((const uint8_t *)text,
                                                 (const uint8_t *)token);
}
int32_t g2_log_module_filter(const char *module,const uint8_t *token)
{
    return (int32_t)g2_log_candidate_find_token((const uint8_t *)module,token);
}
void g2_log_line_five(char out[6],const char *format,uint32_t line)
{
    (void)format;
    (void)g2_log_candidate_timestamp_5((uint8_t *)out,line);
}
