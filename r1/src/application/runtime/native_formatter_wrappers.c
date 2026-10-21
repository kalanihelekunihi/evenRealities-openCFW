#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
typedef uint32_t (*output_fn)(uint32_t,uint32_t);
extern uint32_t r1_format_core(volatile const uint8_t *,volatile uint32_t *,uint32_t,output_fn);
extern uint32_t r1_format_bounded_putc(uint32_t,volatile uint32_t *);
static uint32_t bounded_output(uint32_t byte,uint32_t context)
{ return r1_format_bounded_putc(byte,(volatile uint32_t *)(uintptr_t)context); }
/* Formatting and termination are source C. Assembly below only establishes
 * the recovered native vararg/frame convention and restores context in r2/r3.
 * The worker/parser private frames below it remain a separate alias gate. */
__attribute__((used,noinline)) uint32_t r1_bounded_format_body(uint32_t destination,uint32_t size,
    volatile const uint8_t *format,volatile uint32_t *arguments,volatile uint32_t *context)
{
    context[0]=destination;
    context[1]=size ? size-1u : 0;
    uint32_t count=r1_format_core(format,arguments,(uint32_t)(uintptr_t)context,bounded_output);
    if (size) *(volatile uint8_t *)(uintptr_t)context[0]=0;
    return count;
}
__attribute__((naked)) int snprintf(char *destination __attribute__((unused)),
    size_t size __attribute__((unused)),const char *format __attribute__((unused)),...)
{
    __asm__ volatile("push {r0,r1,r2,r3}\n"
                     "push {r2,r3,r4,r5,r6,lr}\n"
                     "mov r4,r1\n"
                     "mov r12,sp\n"
                     "add r3,sp,#36\n"
                     "ldr r2,[sp,#32]\n"
                     "sub sp,#8\n"
                     "str r12,[sp]\n"
                     "bl r1_bounded_format_body\n"
                     "add sp,#8\n"
                     "cmp r4,#0\n"
                     "it ne\n"
                     "movne r1,#0\n"
                     "pop {r2,r3,r4,r5,r6}\n"
                     "ldr pc,[sp],#20\n");
}
__attribute__((naked)) int vsnprintf(char *destination __attribute__((unused)),
    size_t size __attribute__((unused)),const char *format __attribute__((unused)),va_list arguments __attribute__((unused)))
{
    __asm__ volatile("push {r2,r3,r4,r5,r6,lr}\n"
                     "mov r4,r1\n"
                     "mov r12,sp\n"
                     "sub sp,#8\n"
                     "str r12,[sp]\n"
                     "bl r1_bounded_format_body\n"
                     "add sp,#8\n"
                     "cmp r4,#0\n"
                     "it ne\n"
                     "movne r1,#0\n"
                     "pop {r2,r3,r4,r5,r6,pc}\n");
}

extern __typeof__(snprintf) r1_native_snprintf __attribute__((alias("snprintf")));
extern __typeof__(vsnprintf) r1_native_vsnprintf __attribute__((alias("vsnprintf")));
