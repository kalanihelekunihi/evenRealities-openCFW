#include <stdarg.h>
#include <stdint.h>
_Static_assert(sizeof(va_list) == sizeof(uint32_t), "ARM va_list is not one register word");
extern uint32_t audio_heap_formatter(char *, const char *, va_list);
uint32_t g2_print_abi_probe(char *buffer, const char *format, va_list words) {
    return audio_heap_formatter(buffer, format, words);
}
