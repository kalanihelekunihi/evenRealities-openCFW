#include <stdint.h>

/* Native 0x30fd34: tail alias of the PAL current-time read (native 0x310104). */
extern uint32_t opencfw_em9305_pal_current_time(void);

uint32_t opencfw_em9305_associated_time_alias_30fd34(void)
{
    return opencfw_em9305_pal_current_time();
}
