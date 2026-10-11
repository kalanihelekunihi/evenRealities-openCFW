/* SPDX-License-Identifier: MIT
 * Isolated C reduction of Apollo Main 0x43d574..0x43d976 (1026 bytes).
 * The formatter, fatal continuation, product strings/state and output are
 * typed imports. This is a compiled outer control-flow candidate, not an
 * admitted stock-equivalent logger or a transport implementation.
 */
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include "../../main/extended_log_root_candidate_20261011/extended_log.h"

extern void (*g2_extended_log_fatal_callback)(const char *,const char *,uint32_t);
extern bool g2_log_is_privileged(void);
extern uint32_t g2_log_exception_number(void);
extern uint32_t g2_log_module_policy(const char *);
extern int32_t g2_log_module_filter(const char *,const uint8_t *);
extern uint32_t g2_log_module_length(const char *);
extern void g2_log_guard_enter(void);
extern void g2_log_guard_exit(void);
extern bool g2_log_format_enabled(uint8_t,uint32_t);
extern bool g2_log_source_field_enabled(uint8_t,uint32_t,const void *);
extern const char *g2_log_time_string(void);
extern const char *g2_log_process_string(void);
extern const char *g2_log_thread_string(void);
extern void g2_log_line_five(char out[6],const char *,uint32_t);
extern int32_t g2_log_vformat(char *,uint32_t,const char *,va_list);
extern int32_t g2_log_contains(const char *,const char *);
extern void g2_log_output(const char *,uint32_t,uint8_t);
extern void g2_log_fatal_idle(void) __attribute__((noreturn));

/* The selected logger append helper returns the number of bytes copied.
 * The product buffer's 1024-byte capacity is a required input contract. */
extern uint32_t g2_log_append(uint32_t,char *,const char *);
extern void g2_log_stack_fill(char *,uint32_t,uint8_t);

static uint32_t append(const struct g2_extended_log_product *p,
                       uint32_t used,const char *text)
{
    return used + g2_log_append(used,p->buffer + used,text);
}

void audio_log_extended(uint8_t level,const char *module,
                               const char *file,const char *function,
                               uint32_t line,const char *format,...)
{
    const struct g2_extended_log_product *p = &g2_extended_log_product;
    uint32_t exception = g2_log_is_privileged()
        ? g2_log_exception_number() & 0x1ffu : 0u;
    if (exception != 0u) return;
    if (level > 5u) {
        if (g2_extended_log_fatal_callback == 0) {
            audio_log_extended(0u,p->fatal_module,p->fatal_file,
                                      p->fatal_function,0x23cu,p->fatal_format);
            g2_log_fatal_idle();
        }
        g2_extended_log_fatal_callback(p->fatal_file,p->fatal_function,0x23cu);
    }
    volatile uint8_t *state = p->state;
    if (state[241] == 0u || level > state[0] ||
        level > g2_log_module_policy(module) ||
        g2_log_module_filter(module,(const uint8_t *)(const void *)(state+1)) == 0)
        return;

    uint32_t module_length = g2_log_module_length(module);
    char pad[16],line_text[6];
    g2_log_stack_fill(pad,sizeof(pad),0u);
    g2_log_guard_enter();
    uint32_t used = 0u;
    if (state[245]) {
        used = append(p,used,p->level_prefix);
        used = append(p,used,p->level_headers[level]);
    }
    if (g2_log_format_enabled(level,1u))
        used = append(p,used,p->level_colors[level]);
    if (g2_log_format_enabled(level,2u)) {
        used = append(p,used,module);
        if (module_length < 16u) {
            g2_log_stack_fill(pad,15u-module_length,' ');
            pad[15u-module_length] = 0;
            used = append(p,used,pad);
        }
        used = append(p,used,p->module_suffix);
    }
    if (g2_log_format_enabled(level,0x1cu)) {
        used = append(p,used,p->separator);
        if (g2_log_format_enabled(level,4u)) {
            used = append(p,used,g2_log_time_string());
            if (g2_log_format_enabled(level,0x18u))
                used = append(p,used,p->module_suffix);
        }
        if (g2_log_format_enabled(level,8u)) {
            used = append(p,used,g2_log_process_string());
            if (g2_log_format_enabled(level,0x10u))
                used = append(p,used,p->module_suffix);
        }
        if (g2_log_format_enabled(level,0x10u))
            used = append(p,used,g2_log_thread_string());
        used = append(p,used,p->function_suffix);
    }
    bool show_file = g2_log_source_field_enabled(level,0x20u,file);
    bool show_function = g2_log_source_field_enabled(level,0x40u,function);
    bool show_line = g2_log_source_field_enabled(level,0x80u,&line);
    if (show_file || show_function || show_line) {
        used = append(p,used,p->function_prefix);
        if (show_file) {
            used = append(p,used,file);
            if (show_function) used = append(p,used,p->function_suffix);
            else if (show_line) used = append(p,used,p->module_suffix);
        }
        if (show_line) {
            g2_log_line_five(line_text,p->line_format,line);
            used = append(p,used,line_text);
            if (show_function) used = append(p,used,p->module_suffix);
        }
        if (show_function) used = append(p,used,function);
        used = append(p,used,p->line_suffix);
    }

    va_list arguments;
    va_start(arguments,format);
    int32_t count = g2_log_vformat(p->buffer+used,1024u-used,format,arguments);
    va_end(arguments);
    if (count >= 0 && (uint32_t)count + used <= 1024u) used += (uint32_t)count;
    else used = 1024u;
    if (used + 5u > 1024u) used = 1019u;
    if (state[32] != 0u) {
        p->buffer[used] = 0;
        if (g2_log_contains(p->buffer,(const char *)(const void *)(state+32)) == 0) {
            g2_log_guard_exit();
            return;
        }
    }
    if (state[245]) used = append(p,used,p->normal_suffix);
    used = append(p,used,p->message_suffix);
    g2_log_output(p->buffer,used,level);
    g2_log_guard_exit();
}
