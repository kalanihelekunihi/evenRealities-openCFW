#include <stdint.h>
#include <stdarg.h>
extern uint32_t r1_native_scanf_format_getc(uint32_t *,uint32_t);
extern uint32_t r1_native_isspace(uint32_t);
extern int32_t r1_native_scanf_input_getc(volatile uint32_t *);
extern int32_t r1_native_scanf_input_ungetc(volatile uint32_t *);
/* Explicit unresolved provider: no trap or native executable fallback. */
extern int32_t r1_native_scanf_core(void *,volatile uint32_t *);
int32_t r1_native_scanf_descriptor_init(void *input,const char *format,volatile uint32_t *descriptor)
{
 descriptor[3]=(uint32_t)(uintptr_t)format;
 descriptor[5]=(uint32_t)(uintptr_t)r1_native_scanf_format_getc;
 descriptor[8]=(uint32_t)(uintptr_t)r1_native_isspace;
 descriptor[4]=0;
 return r1_native_scanf_core(input,descriptor);
}
int32_t r1_native_sscanf(const char *input,const char *format,...)
{
 va_list arguments;va_start(arguments,format);
 uint32_t descriptor[9];
 uint32_t input_state[4]={(uint32_t)(uintptr_t)input,UINT32_MAX,(uint32_t)(uintptr_t)input,0};
 /* Pinned ARM AAPCS va_list is a single address word, represented as a
  * compiler builtin aggregate rather than a C pointer by Clang. */
 _Static_assert(sizeof(va_list)==sizeof(uint32_t),"ARM single-word va_list required");
 uint32_t argument_cursor;__builtin_memcpy(&argument_cursor,&arguments,sizeof(argument_cursor));
 descriptor[0]=argument_cursor;
 descriptor[6]=(uint32_t)(uintptr_t)r1_native_scanf_input_getc;
 descriptor[7]=(uint32_t)(uintptr_t)r1_native_scanf_input_ungetc;
 int32_t result=r1_native_scanf_descriptor_init(input_state,format,descriptor);
 va_end(arguments);return result;
}
