/* Main 0x481836 candidate: adapted from pinned IAR Bootloader source;
 * identical 1270-instruction core topology except 23 relocated BL sites. */
#include <stdint.h>
typedef void *(*g2_main_format_put)(void *,uint32_t);
/* IAR ARM32 cursor ABI, not host va_list. Fifth argument is truncated to8bits. */
int32_t g2_iar_general_format(g2_main_format_put,void *,const char *,uint32_t **,unsigned);
