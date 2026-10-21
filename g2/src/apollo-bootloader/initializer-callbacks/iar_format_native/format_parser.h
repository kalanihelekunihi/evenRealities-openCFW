#include <stdint.h>
typedef struct {uint32_t flags;int32_t width,precision;uint32_t length,conversion;} opencfw_format_spec;
const char *opencfw_format_parse(const char *percent,uint32_t **cursor,opencfw_format_spec *out);
/* Cursor words follow the stock ARM32 IAR ABI; no host va_list conversion. */
