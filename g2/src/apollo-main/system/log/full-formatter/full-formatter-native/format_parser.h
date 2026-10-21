/* Main 0x481836 candidate: adapted from pinned IAR Bootloader source;
 * identical 1270-instruction core topology except 23 relocated BL sites. */
#include <stdint.h>
typedef struct {uint32_t flags;int32_t width,precision;uint32_t length,conversion;} g2_main_format_spec;
const char *g2_main_format_parse(const char *percent,uint32_t **cursor,g2_main_format_spec *out);
/* Cursor words follow the stock ARM32 IAR ABI; no host va_list conversion. */
