/*
 * This file is part of the EasyLogger Library.
 *
 * Copyright (c) 2015-2018, Armink, <armink.ztl@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * 'Software'), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * Stock adaptation below: locked bootloader f89a4c46..., repository pin
 * a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24.
 */
#include "elog_setters.h"
#include "service_records.h"
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdarg.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define ELOG_LINE_BUF_SIZE 1024u
#define ELOG_LINE_NUM_MAX_LEN 5u
#define ELOG_FILTER_TAG_MAX_LEN 30u
#define ELOG_LVL_VERBOSE 5u
#define ELOG_NEWLINE_SIGN "\n"
#define ELOG_COLOR_ENABLE
#define CSI_START "\x1b["
#define CSI_END "\x1b[0m"
#define ELOG_FMT_LVL 1u
#define ELOG_FMT_TAG 2u
#define ELOG_FMT_TIME 4u
#define ELOG_FMT_P_INFO 8u
#define ELOG_FMT_T_INFO 16u
#define ELOG_FMT_DIR 32u
#define ELOG_FMT_FUNC 64u
#define ELOG_FMT_LINE 128u
struct tag_slot {uint8_t level;char tag[31];uint8_t active;};
struct logger {struct {uint8_t level;char tag[31];char keyword[17];struct tag_slot slots[5];} filter;
 uint32_t enabled_fmt_set[6];uint8_t initialized,output_enabled,output_lock_enabled,before_enable,before_disable,text_color_enabled;};
_Static_assert(offsetof(struct logger,enabled_fmt_set)==0xd8,"stock format layout");
_Static_assert(offsetof(struct logger,output_enabled)==0xf1,"stock output layout");
#define elog (*(volatile struct logger *)(uintptr_t)0x20026700)
#define log_buf ((char *)(uintptr_t)0x200258d0)
#define color_output_info ((const char **)(uintptr_t)0x20000334)
#define level_output_info ((const char **)(uintptr_t)0x2000031c)
extern size_t strlen(const char *);
extern void *memset(void *,int,size_t);
extern int opencfw_boot_elog_snprintf(char *,size_t,const char *,...);
extern int opencfw_boot_elog_vsnprintf(char *,size_t,const char *,va_list);
extern const char *elog_port_get_time(void);
extern const char *elog_port_get_p_info(void);
extern const char *elog_port_get_t_info(void);
extern void opencfw_boot_elog_uart_output(const char *,size_t,uint32_t);
static char *strstr(const char *hay,const char *needle) {
 if(!*needle)return (char *)hay;
 for(;*hay;hay++){size_t i=0;while(needle[i]&&hay[i]==needle[i])i++;if(!needle[i])return (char *)hay;}
 return 0;
}
void opencfw_boot_elog_lock(void) {if(B(0x200267f2)){opencfw_bl_service_wake();B(0x200267f4)=1;}else B(0x200267f3)=1;}
void opencfw_boot_elog_unlock(void) {if(B(0x200267f2)){opencfw_bl_service_sleep();B(0x200267f4)=0;}else B(0x200267f3)=0;}
uint32_t opencfw_boot_elog_tag_level(const char *tag) {
 if(!tag)opencfw_boot_elog_assert("tag != ((void *)0)","elog_get_filter_tag_lvl",481);
 uint32_t level=5;
 if(!B(0x200267f0))return level;
 opencfw_boot_elog_lock();
 for(uint32_t i=0;i<5;i++){
  volatile struct tag_slot *slot=&elog.filter.slots[i];
  if(slot->active==1){unsigned k=0;while(k<30&&tag[k]==slot->tag[k]){if(!tag[k])break;k++;}
   if(k==30||tag[k]==slot->tag[k]){level=slot->level;break;}}
 }
 opencfw_boot_elog_unlock();return level;
}
void opencfw_boot_elog_output(uint32_t,const char *,const char *,const char *,long,const char *,...);
static void utils_assert(const char *condition,uint32_t line) {
 uint32_t callback=W(0x200270e4);
 if(callback){((void(*)(const char *,const char *,uint32_t))(uintptr_t)callback)(condition,"elog_strcpy",line);return;}
 opencfw_boot_elog_output(0,"elog","D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\EasyLogger-master\\easylogger\\src\\elog_utils.c","elog_strcpy",line,"(%s) has assert failed at %s:%ld.",condition,"elog_strcpy",line);
 opencfw_boot_elog_reset_request();
}
size_t opencfw_boot_elog_append(size_t offset,char *dest,const char *text) {
 if(!dest)utils_assert("dst",44);
 if(!text)utils_assert("src",45);
 const char *start=text;while(*text&&offset++<1024)*dest++=*text++;return (size_t)(text-start);
}
static bool fmt_enabled(uint8_t level,size_t mask) {
 if(level>5)opencfw_boot_elog_assert("level <= ELOG_LVL_VERBOSE","get_fmt_enabled",743);
 return (W(0x200267d8+4u*level)&mask)!=0;
}
static bool fmt_ptr(uint8_t level,size_t mask,const char *p){return p&&fmt_enabled(level,mask);}
static bool fmt_number(uint8_t level,size_t mask,uint32_t p){return p&&fmt_enabled(level,mask);}
void opencfw_boot_elog_output(uint32_t level, const char *tag, const char *file, const char *func,
        const long line, const char *format, ...) {
    extern const char *elog_port_get_time(void);
    extern const char *elog_port_get_p_info(void);
    extern const char *elog_port_get_t_info(void);

    level=(uint8_t)level;
    uint32_t exception; __asm__ volatile("mrs %0, ipsr" : "=r"(exception));
    if(exception) return;
    size_t tag_len, log_len = 0, newline_len = 1;
    char line_num[ELOG_LINE_NUM_MAX_LEN + 1] = { 0 };
    char tag_sapce[ELOG_FILTER_TAG_MAX_LEN / 2 + 1] = { 0 };
    va_list args;
    int fmt_result;

    if(level>5) opencfw_boot_elog_assert("level <= ELOG_LVL_VERBOSE","elog_output",572);

    /* check output enabled */
    if (!elog.output_enabled) {
        return;
    }
    /* level filter */
    if (level > elog.filter.level || level > opencfw_boot_elog_tag_level(tag)) {
        return;
    } else if (!strstr(tag, (const char *)elog.filter.tag)) { /* tag filter */
        return;
    }
    tag_len = strlen(tag);
    /* args point to the first variable parameter */
    va_start(args, format);
    /* lock output */
    opencfw_boot_elog_lock();

#ifdef ELOG_COLOR_ENABLE
    /* add CSI start sign and color info */
    if (elog.text_color_enabled) {
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, CSI_START);
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, color_output_info[level]);
    }
#endif

    /* package level info */
    if (fmt_enabled(level, ELOG_FMT_LVL)) {
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, level_output_info[level]);
    }
    /* package tag info */
    if (fmt_enabled(level, ELOG_FMT_TAG)) {
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, tag);
        /* if the tag length is less than 50% ELOG_FILTER_TAG_MAX_LEN, then fill space */
        if (tag_len <= ELOG_FILTER_TAG_MAX_LEN / 2) {
            memset(tag_sapce, ' ', ELOG_FILTER_TAG_MAX_LEN / 2 - tag_len);
            log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, tag_sapce);
        }
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, " ");
    }
    /* package time, process and thread info */
    if (fmt_enabled(level, ELOG_FMT_TIME | ELOG_FMT_P_INFO | ELOG_FMT_T_INFO)) {
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, "[");
        /* package time info */
        if (fmt_enabled(level, ELOG_FMT_TIME)) {
            log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, elog_port_get_time());
            if (fmt_enabled(level, ELOG_FMT_P_INFO | ELOG_FMT_T_INFO)) {
                log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, " ");
            }
        }
        /* package process info */
        if (fmt_enabled(level, ELOG_FMT_P_INFO)) {
            log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, elog_port_get_p_info());
            if (fmt_enabled(level, ELOG_FMT_T_INFO)) {
                log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, " ");
            }
        }
        /* package thread info */
        if (fmt_enabled(level, ELOG_FMT_T_INFO)) {
            log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, elog_port_get_t_info());
        }
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, "] ");
    }
    /* package file directory and name, function name and line number info */
    if (fmt_ptr(level, ELOG_FMT_DIR, file) ||
            fmt_ptr(level, ELOG_FMT_FUNC, func) ||
            fmt_number(level, ELOG_FMT_LINE, line)) {
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, "(");
        /* package file info */
        if (fmt_ptr(level, ELOG_FMT_DIR, file)) {
            log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, file);
            if (fmt_ptr(level, ELOG_FMT_FUNC, func)) {
                log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, ":");
            } else if (fmt_number(level, ELOG_FMT_LINE, line)) {
                log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, " ");
            }
        }
        /* package line info */
        if (fmt_number(level, ELOG_FMT_LINE, line)) {
            opencfw_boot_elog_snprintf(line_num, ELOG_LINE_NUM_MAX_LEN, "%ld", line);
            log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, line_num);
            if (fmt_ptr(level, ELOG_FMT_FUNC, func)) {
                log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, " ");
            }
        }
        /* package func info */
        if (fmt_ptr(level, ELOG_FMT_FUNC, func)) {
            log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, func);
            
        }
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, ")");
    }
    /* package other log data to buffer. '\0' must be added in the end by vsnprintf. */
    fmt_result = opencfw_boot_elog_vsnprintf(log_buf + log_len, ELOG_LINE_BUF_SIZE - log_len, format, args);

    va_end(args);
    /* calculate log length */
    if ((log_len + fmt_result <= ELOG_LINE_BUF_SIZE) && (fmt_result > -1)) {
        log_len += fmt_result;
    } else {
        /* using max length */
        log_len = ELOG_LINE_BUF_SIZE;
    }
    /* overflow check and reserve some space for CSI end sign and newline sign */
#ifdef ELOG_COLOR_ENABLE
    if (log_len + (sizeof(CSI_END) - 1) + newline_len > ELOG_LINE_BUF_SIZE) {
        /* using max length */
        log_len = ELOG_LINE_BUF_SIZE;
        /* reserve some space for CSI end sign */
        log_len -= (sizeof(CSI_END) - 1);
#else
    if (log_len + newline_len > ELOG_LINE_BUF_SIZE) {
        /* using max length */
        log_len = ELOG_LINE_BUF_SIZE;
#endif /* ELOG_COLOR_ENABLE */
        /* reserve some space for newline sign */
        log_len -= newline_len;
    }
    /* keyword filter */
    if (elog.filter.keyword[0] != '\0') {
        /* add string end sign */
        log_buf[log_len] = '\0';
        /* find the keyword */
        if (!strstr(log_buf, (const char *)elog.filter.keyword)) {
            /* unlock output */
            opencfw_boot_elog_unlock();
            return;
        }
    }

#ifdef ELOG_COLOR_ENABLE
    /* add CSI end sign */
    if (elog.text_color_enabled) {
        log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, CSI_END);
    }
#endif

    /* package newline sign */
    log_len += opencfw_boot_elog_append(log_len, log_buf + log_len, ELOG_NEWLINE_SIGN);
    /* output log */
#if defined(ELOG_ASYNC_OUTPUT_ENABLE)
    extern void elog_async_output(uint8_t level, const char *log, size_t size);
    elog_async_output(level, log_buf, log_len);
#elif defined(ELOG_BUF_OUTPUT_ENABLE)
    extern void elog_buf_output(const char *log, size_t size);
    elog_buf_output(log_buf, log_len);
#else
    opencfw_boot_elog_uart_output(log_buf, log_len, level);
#endif
    /* unlock output */
    opencfw_boot_elog_unlock();
}


/* Metadata wrappers41a6aa/41a6c2/41a6f0/41a6f8. Raw kernel ticks, no ms conversion. */
extern uint32_t opencfw_boot_current_task(void);
extern uint32_t opencfw_bl_queue_runtime_mode(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
static const char *thread_name(void) {
 if(opencfw_bl_queue_runtime_mode()==1)return "unknown";
 uint32_t task=opencfw_boot_current_task();
 if(!task){(void)opencfw_bl_mask_interrupts();W(0xffffffff)=0;for(;;)__asm__ volatile("nop");}
 return (const char *)(uintptr_t)(task+0x34);
}
const char *elog_port_get_p_info(void){return thread_name();}
const char *elog_port_get_t_info(void){return thread_name();}
const char *elog_port_get_time(void){
 opencfw_boot_elog_snprintf((char *)(uintptr_t)0x20026f18,28,"%d",W(0x20027148));
 return (const char *)(uintptr_t)0x20026f18;
}
