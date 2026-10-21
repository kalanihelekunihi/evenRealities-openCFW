/* SPDX-License-Identifier: MIT
 * Experimental composition of the logger outer candidate with selected
 * bounded Main helpers. Product state, formatting and transport stay imports.
 */
#include "extended_log.h"
#include <stdbool.h>
#include <stdint.h>

extern uint32_t g2_log_candidate_append_normal(uint32_t,uint8_t *,const uint8_t *);
extern uint32_t g2_log_candidate_module_length(const uint8_t *);
extern uint32_t g2_log_candidate_find_token(const uint8_t *,const uint8_t *);
extern uint32_t g2_log_candidate_timestamp_5(uint8_t *,uint32_t);
extern void g2_log_candidate_stack_fill(uint8_t *,uint32_t,uint32_t);
typedef struct { void (*enter)(void); void (*exit)(void); } guard_hooks;
typedef struct { void (*submit)(uint32_t,uint32_t,uint32_t,uint32_t);
                 void (*signal)(uint32_t,uint32_t); } output_hooks;
extern void g2_log_candidate_guard_enter(void *);
extern void g2_log_candidate_guard_exit(void *);
extern uint32_t g2_log_candidate_module_policy(const guard_hooks *,uint32_t);
extern void g2_log_candidate_output(const output_hooks *,uint32_t,uint32_t,uint32_t);
/* Actual lock and output transport implementations remain image contracts. */
extern void g2_log_lock_enter(void),g2_log_lock_exit(void);
extern void g2_log_transport_submit(uint32_t,uint32_t,uint32_t,uint32_t);
extern void g2_log_transport_signal(uint32_t,uint32_t);
static const guard_hooks guard = {g2_log_lock_enter,g2_log_lock_exit};
static const output_hooks output = {g2_log_transport_submit,g2_log_transport_signal};

void g2_log_stack_fill(char *destination,uint32_t count,uint8_t value)
{
    g2_log_candidate_stack_fill((uint8_t *)destination,count,value);
}

void g2_log_guard_enter(void) { g2_log_candidate_guard_enter((void *)&guard); }
void g2_log_guard_exit(void) { g2_log_candidate_guard_exit((void *)&guard); }
uint32_t g2_log_module_policy(const char *module)
{
    return g2_log_candidate_module_policy(&guard,(uint32_t)(uintptr_t)module);
}
void g2_log_output(const char *buffer,uint32_t length,uint8_t level)
{
    g2_log_candidate_output(&output,(uint32_t)(uintptr_t)buffer,length,level);
}

uint32_t g2_log_append(uint32_t offset,char *destination,const char *source)
{
    return g2_log_candidate_append_normal(offset,(uint8_t *)destination,
                                           (const uint8_t *)source);
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
bool g2_log_format_enabled(uint8_t level,uint32_t mask)
{
    const volatile uint32_t *words = (const volatile uint32_t *)(const void *)
        (g2_extended_log_product.state + 216u);
    return (words[level] & mask) != 0u;
}
bool g2_log_source_field_enabled(uint8_t level,uint32_t mask,const void *value)
{
    return value != 0 && g2_log_format_enabled(level,mask);
}
void g2_log_line_five(char out[6],const char *format,uint32_t line)
{
    (void)format;
    (void)g2_log_candidate_timestamp_5((uint8_t *)out,line);
}
