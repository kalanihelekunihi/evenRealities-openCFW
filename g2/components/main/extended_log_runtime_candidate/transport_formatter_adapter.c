/* Stock 0x473036 three-argument vformatter maps to the already selected
 * Ambiq-derived audio_heap_formatter body. Both take dest, format, va_list. */
#include <stdint.h>
#include <stdarg.h>
extern uint32_t audio_heap_formatter(char *dest,const char *format,va_list args);
int32_t g2_log_transport_vformat_unbounded(char *dest,const char *format,
                                            va_list args) {
    return (int32_t)audio_heap_formatter(dest,format,args);
}

/* Main FlashDB print wrapper passes three ARM words: buffer, format and
 * va_list word pointer. Its authenticated callee is the same 0x473036. */
int32_t g2_flashdb_vformat(uint32_t buffer,uint32_t format,
                           uint32_t arguments) {
    _Static_assert(sizeof(va_list)==4,"ARM32 va_list word ABI");
    va_list list;
    __builtin_memcpy(&list,&arguments,sizeof(list));
    return (int32_t)audio_heap_formatter((char *)(uintptr_t)buffer,
                                         (const char *)(uintptr_t)format,list);
}
