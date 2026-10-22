/* Bounce animation ownership query, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\anim\bounce_anim.c.
 * Native 0x58a83e..0x58a857; literal pool word 0x58a86c.
 *
 * The rest of bounce_anim.c is app/conversate-bounce (0x58a408..0x58a83d).
 * The teleprompt file menu calls this as teleprompt_is_current_file_58a83e
 * (ui/a-53-teleprompt-ui) to ask whether its list is still bouncing. */
#include <stdint.h>

/* +0x00 object currently bouncing (0 none), +0x04 its start y. */
extern volatile uint8_t audio_conversate_bounce_state_20073e14[16]; /* RAM 0x20073e14 */

uint8_t teleprompt_is_current_file_58a83e(const void *obj)
{
    if (obj == 0)
        return 0u;
    const volatile uint32_t *state = (const volatile uint32_t *)(const volatile void *)audio_conversate_bounce_state_20073e14;
    return state[0] == (uint32_t)(uintptr_t)obj ? 1u : 0u;
}
