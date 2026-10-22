/* List animation "running" query, part of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\anim\list_anim.c.
 * Native 0x5897e0..0x5897ed (pool word 0x589934 shared with the rest of the
 * file, see app/terminal-list). Runs the timeout recovery first, then
 * returns the animating flag (+0xc3) of the list-animation state (RAM
 * 0x20070ea8). The teleprompt file list uses it to ignore input while a
 * list scroll animation is in progress. */
#include <stdint.h>

extern uint8_t audio_terminal_list_anim_state_base[0xd0]; /* RAM 0x20070ea8 */
extern void audio_terminal_list_anim_timeout_poll_5893fe(void);

uint8_t teleprompt_file_request_busy_5897e0(void)
{
    audio_terminal_list_anim_timeout_poll_5893fe();
    return audio_terminal_list_anim_state_base[0xc3u];
}
