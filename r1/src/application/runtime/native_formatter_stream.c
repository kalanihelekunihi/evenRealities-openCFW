#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
typedef uint32_t (*output_fn)(uint32_t,uint32_t);
extern uint32_t r1_format_core(volatile const uint8_t *,volatile uint32_t *,uint32_t,output_fn);
extern uint32_t r1_stdout_write(uint32_t,volatile void *,uint32_t);
uint32_t r1_format_unbounded_putc(uint32_t byte,volatile uint32_t *context)
{
    uint32_t destination=context[0],next=destination+1u;
    context[0]=next;
    *(volatile uint8_t *)(uintptr_t)destination=(uint8_t)byte;
    return byte;
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
/* Arm Clang's AAPCS va_list contains the saved argument cursor. The formatter
 * consumes the same word stream that the former entry frame exposed. */
_Static_assert(sizeof(va_list)==sizeof(uintptr_t),"Arm varargs cursor ABI");
static volatile uint32_t *argument_words(va_list *arguments)
{
    uintptr_t cursor;
    __builtin_memcpy(&cursor,arguments,sizeof(cursor));
    return (volatile uint32_t *)cursor;
}
int sprintf(char *destination,const char *format,...)
{
    va_list arguments;
    va_start(arguments,format);
    volatile uint32_t context[1]={(uint32_t)(uintptr_t)destination};
    volatile uint32_t result[3];
    r1_sprintf_body((const volatile uint8_t *)format,
                    argument_words(&arguments),context,result);
    va_end(arguments);
    return (int)result[0];
}
uint32_t r1_format_stdout_putc(uint32_t byte,uint32_t context)
{
    volatile uint32_t record[2]={byte,context};
    (void)r1_stdout_write(0,(volatile void *)record,1);
    return record[0];
}
__attribute__((used,noinline)) uint32_t r1_printf_body(volatile const uint8_t *format,volatile uint32_t *arguments)
{ return r1_format_core(format,arguments,UINT32_C(0x20007db8),r1_format_stdout_putc); }
int printf(const char *format,...)
{
    va_list arguments;
    va_start(arguments,format);
    uint32_t count=r1_printf_body((const volatile uint8_t *)format,
                                  argument_words(&arguments));
    va_end(arguments);
    return (int)count;
}
extern __typeof__(sprintf) r1_native_sprintf __attribute__((alias("sprintf")));
extern __typeof__(printf) r1_native_printf __attribute__((alias("printf")));
