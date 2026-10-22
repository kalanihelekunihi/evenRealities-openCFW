/* Terminal session-list selection payload packer, native 0x5eca32..0x5eca3e
 * (no literal pool; no source path retained), between 0x5eca00 and the
 * unpackers 0x5eca3e (audio_terminal_session_command_5eca3e) and 0x5eca44
 * (audio_terminal_session_index_i16_5eca44), which live in
 * app/terminal-session. terminal_ui_input.c (0x5e7878) posts the packed word
 * with event 0x1d; terminal_ui_action_session_list_select/_show (0x5ed4f8,
 * 0x5ed208) unpack it: bits 16..23 = row kind, bits 0..15 = signed row index. */
#include <stdint.h>

uint32_t terminal_session_select_pack_5eca32(uint8_t kind, int16_t index)
{
    return ((uint32_t)kind << 16) | (uint16_t)index;
}
