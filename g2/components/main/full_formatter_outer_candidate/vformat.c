/* Main 0x44b76c buffer wrapper and 0x439c8a output callback.
 * The 0x481836 general formatter remains a typed full-grammar lower contract. */
#include <stdint.h>
#include <stdarg.h>

typedef struct {
    char *cursor;
    uint32_t available;
    uint32_t written;
} g2_format_output;

static g2_format_output *g2_format_put(g2_format_output *out,uint32_t byte) {
    out->written++;
    if(out->available) {
        *out->cursor++=(char)byte;
        out->available--;
    }
    return out;
}

typedef g2_format_output *(*g2_format_put_fn)(g2_format_output *,uint32_t);
extern int32_t g2_iar_general_format(g2_format_put_fn,g2_format_output *,
                                      const char *,uint32_t **,uint32_t);

int32_t g2_log_vformat(char *destination,uint32_t capacity,
                       const char *format,va_list arguments) {
    _Static_assert(sizeof(va_list)==4,"ARM32 IAR cursor ABI only");
    g2_format_output out={capacity?destination:0,capacity?capacity-1u:0u,0u};
    uint32_t *cursor;
    __builtin_memcpy(&cursor,&arguments,sizeof(cursor));
    int32_t result=g2_iar_general_format(g2_format_put,&out,format,&cursor,0u);
    if(out.cursor) *out.cursor=0;
    return result<0?result:(int32_t)out.written;
}
