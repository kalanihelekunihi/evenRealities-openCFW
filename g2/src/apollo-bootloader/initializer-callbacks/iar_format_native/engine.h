#include <stdint.h>
typedef void *(*opencfw_format_put)(void *,uint32_t);
/* IAR ARM32 cursor ABI, not host va_list. Fifth argument is truncated to8bits. */
int32_t opencfw_iar_format_engine(opencfw_format_put,void *,const char *,uint32_t **,unsigned);
