#ifndef G2_IAR_RUNTIME_CANDIDATES_H
#define G2_IAR_RUNTIME_CANDIDATES_H
#include <stdint.h>
typedef uint32_t (*g2_output_callback)(uint32_t, uint32_t);
typedef int32_t (*g2_scan_callback)(uint32_t, int32_t, uint32_t);
typedef struct { uint32_t context, opaque4, opaque8, consumed, width; } g2_scan_state;
typedef struct { uint32_t opaque0, opaque4, context, opaque12[8], count; } g2_output_state;
int32_t g2_isxdigit(int32_t);
uint8_t *g2_strcat(uint8_t *, const uint8_t *);
uint32_t g2_strcspn(const uint8_t *, const uint8_t *);
uint32_t g2_strspn(const uint8_t *, const uint8_t *);
uint8_t *g2_strrchr(const uint8_t *, int32_t);
int32_t g2_putchars(g2_output_callback, g2_output_state *, const uint8_t *, uint32_t);
int32_t g2_getn(g2_scan_callback, g2_scan_state *);
void g2_ungetn(g2_scan_callback, g2_scan_state *, int32_t);
int32_t g2_ranmatch(const uint8_t *, int32_t, uint32_t);
/* Explicit r9 binding: caller supplies original static-base value. Descriptor
 * nonzero lengths must be >=4; terminator consumes its length word only. */
const uint32_t *g2_zero_init3(const uint32_t *, uint32_t);
#endif
