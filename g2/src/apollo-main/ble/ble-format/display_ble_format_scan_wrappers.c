/* Apollo Main native 0x4b4728 and 0x475fc0 IAR variadic wrappers.
 * The formatter engine is the selected native-derived Main candidate.
 * The 0x4d1638 scanner engine remains a genuine unresolved lower. */
#include <stdint.h>
#include <stdarg.h>

typedef void *(*format_put_fn)(void *, uint32_t);
extern int32_t g2_iar_general_format(format_put_fn, void *, const char *,
                                     uint32_t **, uint32_t);
extern int32_t audio_ble_scan_core(int32_t (*)(void *,uint32_t,uint32_t),
                                   void *,const char *,uint32_t **,uint32_t);

static void *format_put(void *context,uint32_t character) {
    char **cursor=(char **)context;
    *(*cursor)++=(char)character;
    return context;
}

static int32_t scan_get(void *context,uint32_t character,uint32_t advance) {
    const char **cursor=(const char **)context;
    if(!advance) { --*cursor; return (int32_t)character; }
    if(!**cursor) return -1;
    return (uint8_t)*(*cursor)++;
}

/* Stock 0x004B4728 (IAR DLIB sprintf) */
int32_t audio_ble_format_to_buffer(char *destination,const char *format,...) {
    va_list arguments;
    va_start(arguments,format);
    _Static_assert(sizeof(va_list)==sizeof(uint32_t *),"ARM32 cursor ABI");
    uint32_t *cursor;
    __builtin_memcpy(&cursor,&arguments,sizeof(cursor));
    char *output=destination;
    int32_t status=g2_iar_general_format(format_put,&output,format,&cursor,0);
    *output=0;
    va_end(arguments);
    return status<0?status:(int32_t)(output-destination);
}

/* Stock 0x00475FC0 (IAR DLIB sscanf) */
int32_t audio_ble_parse_version(const char *input,const char *format,...) {
    va_list arguments;
    va_start(arguments,format);
    _Static_assert(sizeof(va_list)==sizeof(uint32_t *),"ARM32 cursor ABI");
    uint32_t *cursor;
    __builtin_memcpy(&cursor,&arguments,sizeof(cursor));
    const char *source=input;
    int32_t result=audio_ble_scan_core(scan_get,&source,format,&cursor,0);
    va_end(arguments);
    return result;
}
