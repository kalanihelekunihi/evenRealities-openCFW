#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
typedef uint32_t (*output_fn)(uint32_t,uint32_t);
extern uint32_t r1_format_core(volatile const uint8_t *,volatile uint32_t *,uint32_t,output_fn);
extern uint32_t r1_format_bounded_putc(uint32_t,volatile uint32_t *);
static uint32_t bounded_output(uint32_t byte,uint32_t context)
{ return r1_format_bounded_putc(byte,(volatile uint32_t *)(uintptr_t)context); }
/* Ordinary C variadic entries use the selected Arm AAPCS va_list layout.
 * Caller-clobbered registers and private frame placement are not API outputs. */
__attribute__((used,noinline)) uint32_t r1_bounded_format_body(uint32_t destination,uint32_t size,
    volatile const uint8_t *format,volatile uint32_t *arguments,volatile uint32_t *context)
{
    context[0]=destination;
    context[1]=size ? size-1u : 0;
    uint32_t count=r1_format_core(format,arguments,(uint32_t)(uintptr_t)context,bounded_output);
    if (size) *(volatile uint8_t *)(uintptr_t)context[0]=0;
    return count;
}
/* The pinned Arm Clang va_list is a single argument-stream pointer. Copy its
 * object representation rather than depending on a compiler field name. */
_Static_assert(sizeof(va_list)==sizeof(uint32_t *),"Arm AAPCS va_list pointer ABI");
static volatile uint32_t *argument_words(va_list arguments)
{
    volatile uint32_t *words;
    __builtin_memcpy(&words,&arguments,sizeof words);
    return words;
}
int snprintf(char *destination,size_t size,const char *format,...)
{
    va_list arguments;va_start(arguments,format);
    volatile uint32_t context[2];
    uint32_t count=r1_bounded_format_body((uint32_t)(uintptr_t)destination,
        (uint32_t)size,(volatile const uint8_t *)format,argument_words(arguments),context);
    va_end(arguments);
    return (int)count;
}
int vsnprintf(char *destination,size_t size,const char *format,va_list arguments)
{
    volatile uint32_t context[2];
    return (int)r1_bounded_format_body((uint32_t)(uintptr_t)destination,
        (uint32_t)size,(volatile const uint8_t *)format,argument_words(arguments),context);
}

extern __typeof__(snprintf) r1_native_snprintf __attribute__((alias("snprintf")));
extern __typeof__(vsnprintf) r1_native_vsnprintf __attribute__((alias("vsnprintf")));
