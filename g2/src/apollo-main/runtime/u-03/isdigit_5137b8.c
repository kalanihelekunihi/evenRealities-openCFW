/* IAR DLIB <ctype.h> isdigit, out-of-line copy (no source path retained).
 * Native 0x5137b8..0x5137c2. Callers: storage/nvdb/service_nvdb_sys_dt.c (PSN digits). */
#include <stdint.h>

int32_t isdigit_5137b8(int32_t c)
{
    return (uint32_t)(c - '0') < 10u;
}
