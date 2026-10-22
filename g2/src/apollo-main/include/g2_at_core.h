/* eAT command core, stock platform\service\eAT\core\at_core.c
 * (native 0x5412e0..0x541579). */
#ifndef G2_AT_CORE_H
#define G2_AT_CORE_H
#include <stdint.h>

/* Command handler: text after "=" split once more on "=" (NULL when absent). */
typedef int32_t (*g2_at_handler_t)(const char *arg1, const char *arg2);
/* Output sink: formatted reply text and its length. */
typedef void (*g2_at_output_t)(const char *text, int32_t length);

/* Registry row (linker table ROM 0x6c9260..0x6c93af, 21 rows of 16 bytes). */
typedef struct {
    uint8_t type;            /* +0x0 bit0 allowed in restricted mode, bit1 run on a worker thread */
    const char *name;        /* +0x4 e.g. "AT^INFO" */
    g2_at_handler_t handler; /* +0x8 */
    uint32_t reserved;       /* +0xc always 0 */
} g2_at_cmd_t;
_Static_assert(sizeof(g2_at_cmd_t) == 16, "stock AT registry row is 16 bytes");

enum {
    G2_AT_CMD_RESTRICTED_OK = 1u,
    G2_AT_CMD_ASYNC = 2u,
};

#define G2_AT_OUTPUT_CHANNELS 3u

void at_core_register_callback(uint8_t channel, g2_at_output_t output);
void AT_CoreInit(void);
void AT_Handler(char *command);
void at_core_output(const char *fmt, ...);
void at_core_dispatch_command(const char *command, const char *arg1, const char *arg2);

#endif
