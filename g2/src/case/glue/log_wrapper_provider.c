#include <stdint.h>
#include <stdarg.h>
_Static_assert(sizeof(va_list)==sizeof(void *),"ARM AAPCS va_list pointer word");

extern int32_t case_vformat(const char *format,const uint32_t *arguments,
                            void *context,int32_t (*emit)(int32_t,void *));
extern uint32_t case_write_controller_blocking(void *uart,const uint8_t *byte,
                                                uint32_t length,uint32_t timeout);

/* Original 0x0800a380: one formatted output character goes through the
 * UART byte writer. The writer result is ignored; the character is returned. */
int32_t case_log_output_char(int32_t character,void *context)
{
    (void)context;
    uint8_t byte=(uint8_t)character;
    (void)case_write_controller_blocking((void *)(uintptr_t)0x20000e24u,
                                          &byte,1u,0xffffu);
    return character;
}

/* Original 0x08009170. ARM AAPCS varargs make the register arguments and
 * caller stack continuation one contiguous argument word stream. */
/* Stock 0x08009170 (g2_log_printf) */
int32_t g2_log_printf(const char *format,...)
{
    va_list arguments;
    va_start(arguments,format);
    const uint32_t *words=*(const uint32_t *const *)(const void *)&arguments;
    int32_t count=case_vformat(format,words,
                                (void *)(uintptr_t)0x200001a0u,
                                case_log_output_char);
    va_end(arguments);
    return count;
}
