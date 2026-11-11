#include "instance.h"
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20074b08[] __asm__("g2_stock_ram_20074b08");
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern void uart_thread_handler(void *argument);
extern void *osThreadNew(void (*function)(void *),void *argument,const void *attributes);
extern uint32_t platform_log_flags(void);
extern void platform_log_error(uint32_t level,const void *module,const void *file,
                               const void *format,uint32_t line,const void *function);
extern void compressed_log_output(uint32_t mask,const void *message,const void *message_copy);
/* Stock 0x75c1ec osThreadAttr_t (read from bin/stk12.bin, sim15):
 * {name=0x7846a8 "uart_sync_thread", attr_bits=0, cb_mem=0x20072530, cb_size=0x70,
 *  stack_mem=0x20370e40, stack_size=0x1000, priority=0x2a, tz=0, reserved=0}.
 * cb/stack are stock-RAM buffers; here they are our own statics of the same size. */
static uint32_t g2_uart_sync_cb[0x70/4] __attribute__((aligned(8)));
static uint64_t g2_uart_sync_stack[0x1000/8];
static const struct {const char *name;uint32_t attr_bits;void *cb_mem;uint32_t cb_size;
 void *stack_mem;uint32_t stack_size;uint32_t priority;uint32_t tz_module;uint32_t reserved;}
 g2_uart_sync_attr={"uart_sync_thread",0,g2_uart_sync_cb,0x70,g2_uart_sync_stack,0x1000,0x2a,0,0};
/* Stock strings 0x7846d0/0x710b64/0x7846e4/0x75c1c8/0x72fa80 (bin/stk12.bin). */
static const char g2_ui_mod[]="sync.module.uart";
static const char g2_ui_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\uart_sync.c";
static const char g2_ui_fn[]="uart_instance_init";
static const char g2_ui_msg[]="Failed to create uart sync thread";
static const char g2_ui_short[]="[sync.module.uart]Failed to create uart sync thread";
int32_t uart_instance_init(void){
 void *thread=osThreadNew(uart_thread_handler,0,&g2_uart_sync_attr);
 W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074b08+0x4u))=(uint32_t)(uintptr_t)thread;
 if(thread)return 0;
 if(platform_log_flags()&2u)
  platform_log_error(1,g2_ui_mod,
    g2_ui_file,g2_ui_fn,
    197,g2_ui_msg);
 if((platform_log_flags()&1u)||(platform_log_flags()&4u))
  compressed_log_output(0x04000000u,g2_ui_short,
    g2_ui_short);
 return -1;
}
