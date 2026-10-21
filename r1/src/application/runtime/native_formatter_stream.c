#include <stdint.h>
#include <stddef.h>
typedef uint32_t (*output_fn)(uint32_t,uint32_t);
extern uint32_t r1_format_core(volatile const uint8_t *,volatile uint32_t *,uint32_t,output_fn);
extern uint32_t r1_stdout_write(uint32_t,volatile void *,uint32_t);
uint32_t r1_format_unbounded_putc(uint32_t byte,volatile uint32_t *context)
{
    uint32_t destination=context[0],next=destination+1u;
    context[0]=next;
    *(volatile uint8_t *)(uintptr_t)destination=(uint8_t)byte;
    register uint32_t r0 __asm__("r0")=byte,r1 __asm__("r1")=(uint32_t)(uintptr_t)context;
    register uint32_t r2 __asm__("r2")=destination,r3 __asm__("r3")=next;
    __asm__ volatile("" : "+r"(r0),"+r"(r1),"+r"(r2),"+r"(r3) : : "memory");
    return r0;
}
static uint32_t unbounded_output(uint32_t byte,uint32_t context)
{ return r1_format_unbounded_putc(byte,(volatile uint32_t *)(uintptr_t)context); }
__attribute__((used,noinline)) void r1_sprintf_body(volatile const uint8_t *format,
    volatile uint32_t *arguments,volatile uint32_t *context,volatile uint32_t *result)
{
    uint32_t count=r1_format_core(format,arguments,(uint32_t)(uintptr_t)context,unbounded_output);
    uint32_t destination=context[0];
    (void)r1_format_unbounded_putc(0,context);
    result[0]=count;result[1]=destination;result[2]=destination+1u;
}
__attribute__((naked)) int sprintf(char *destination __attribute__((unused)),
    const char *format __attribute__((unused)),...)
{
    __asm__ volatile("push {r0,r1,r2,r3}\n"
                     "push {r4,lr}\n"
                     "mov r4,sp\n"
                     "sub sp,#16\n"
                     "mov r3,sp\n"
                     "add r2,r4,#8\n"
                     "add r1,r4,#16\n"
                     "ldr r0,[r4,#12]\n"
                     "bl r1_sprintf_body\n"
                     "ldr r0,[sp]\n"
                     "ldr r2,[sp,#4]\n"
                     "ldr r3,[sp,#8]\n"
                     "add r1,r4,#8\n"
                     "add sp,#16\n"
                     "pop {r4}\n"
                     "ldr pc,[sp],#20\n");
}
__attribute__((used,noinline)) uint32_t r1_stdout_byte_body(volatile uint32_t *record)
{
    (void)r1_stdout_write(0,(volatile void *)record,1);
    return record[0];
}
__attribute__((naked)) uint32_t r1_format_stdout_putc(uint32_t byte __attribute__((unused)),uint32_t context __attribute__((unused)))
{
    __asm__ volatile("push {r0,r1,r4,lr}\n"
                     "mov r0,sp\n"
                     "bl r1_stdout_byte_body\n"
                     "pop {r2,r3,r4,pc}\n");
}
__attribute__((used,noinline)) uint32_t r1_printf_body(volatile const uint8_t *format,volatile uint32_t *arguments)
{ return r1_format_core(format,arguments,UINT32_C(0x20007db8),r1_format_stdout_putc); }
__attribute__((naked)) int printf(const char *format __attribute__((unused)),...)
{
    __asm__ volatile("push {r0,r1,r2,r3}\n"
                     "push {r4,lr}\n"
                     "add r1,sp,#12\n"
                     "ldr r0,[sp,#8]\n"
                     "bl r1_printf_body\n"
                     "pop {r4}\n"
                     "ldr pc,[sp],#20\n");
}
extern __typeof__(sprintf) r1_native_sprintf __attribute__((alias("sprintf")));
extern __typeof__(printf) r1_native_printf __attribute__((alias("printf")));
