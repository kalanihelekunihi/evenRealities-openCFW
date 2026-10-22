/* Terminal session selector navigation helpers, native 0x5ed0b8..0x5ed151
 * and 0x5ed152..0x5ed1d5 (between the list rebuild 0x5ecef6 and the root
 * hide 0x5ed1d6 of the terminal session list UI).
 *
 * Both are called from the terminal input handler 0x5e7324 while the session
 * list is shown: input 0x44 (previous) / 0x45 (next) moves the selection,
 * input 0x0a (click) classifies the selected row. Row -1 is the
 * "new session" entry above the session rows. Session records are 0x90 bytes
 * in the active terminal-data block, session id word at +0x9c + 0x90 * row;
 * the block's current session id is at +0x4. */
#include <stdint.h>

#define TERMINAL_INPUT_PREV 0x44u
#define TERMINAL_INPUT_NEXT 0x45u

#define SESSION_ROW_STRIDE  0x90u
#define SESSION_ROW_ID      0x9cu
#define TD_CURRENT_ID       0x04u

/* Row kinds returned by terminal_session_row_kind_5ed152. */
#define SESSION_ROW_NONE    0u
#define SESSION_ROW_CURRENT 1u
#define SESSION_ROW_OTHER   2u
#define SESSION_ROW_NEW     3u

extern uint32_t audio_terminal_session_count_5eca48(void);
extern uint32_t audio_terminal_session_valid_5eca64(int32_t row);
extern uint8_t terminal_host_streaming_ready_5eca84(void); /* BLE up and terminal state 2 */
extern uint8_t *audio_td_active_session(void);           /* 0x59732a td_active_session */
extern uint32_t td_has_active_session(void);             /* 0x5973b2 */

int16_t terminal_session_list_step_5ed0b8(int16_t row, uint32_t input);
uint8_t terminal_session_row_kind_5ed152(int16_t row);

static uint32_t word_at(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) |
           ((uint32_t)p[3] << 24);
}

/* New selection for a previous/next input; other inputs keep the row. */
int16_t terminal_session_list_step_5ed0b8(int16_t row, uint32_t input)
{
    uint32_t const count = audio_terminal_session_count_5eca48();

    if (td_has_active_session() == 0u)
        return row;
    if (input == TERMINAL_INPUT_PREV) {
        if (row == -1)
            return row;
        if (row >= 1)
            return (int16_t)(row - 1);
        if (row == 0)
            return -1;
        return row;
    }
    if (input == TERMINAL_INPUT_NEXT) {
        if (row == -1)
            return count != 0u ? 0 : row;
        if (count == 0u || row < 0)
            return row;
        if ((uint32_t)(row + 1) < count)
            return (int16_t)(row + 1);
        return row;
    }
    return row;
}

uint8_t terminal_session_row_kind_5ed152(int16_t row)
{
    uint8_t *const active = audio_td_active_session();
    uint8_t const ready = terminal_host_streaming_ready_5eca84();
    uint32_t id;

    if (td_has_active_session() == 0u)
        return SESSION_ROW_NONE;
    if (row == -1)
        return ready != 0u ? SESSION_ROW_NEW : SESSION_ROW_NONE;
    if (active == 0 || audio_terminal_session_valid_5eca64(row) == 0u)
        return SESSION_ROW_NONE;
    id = word_at(active + SESSION_ROW_ID + SESSION_ROW_STRIDE * (uint32_t)(int32_t)row);
    /* Without the link only the current session row is selectable. */
    if (ready == 0u && id != word_at(active + TD_CURRENT_ID))
        return SESSION_ROW_NONE;
    return id == word_at(active + TD_CURRENT_ID) ? SESSION_ROW_CURRENT : SESSION_ROW_OTHER;
}
