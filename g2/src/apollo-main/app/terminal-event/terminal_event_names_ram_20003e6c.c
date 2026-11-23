/* Stock terminal event-name lookup reads thirteen pointers at 0x20003e6c.
 * Stock .data initialises them with the ROM name strings (init image
 * 0x20003e6c..0x20003e9f); nothing writes the table at runtime. */
#include <stdint.h>

const char *audio_terminal_event_names[13]
    __attribute__((section(".data.opencfw.terminal.event_names"), aligned(4), used)) = {
    "TERMINAL_EVENT_NONE", /* ROM 0x784068 */
    "TERMINAL_EVENT_MODE_SYNC", /* ROM 0x77315c */
    "TERMINAL_EVENT_HOST_STATUS", /* ROM 0x773178 */
    "TERMINAL_EVENT_ASR_RESULT", /* ROM 0x773194 */
    "TERMINAL_EVENT_SESSION_STATUS", /* ROM 0x7662d0 */
    "TERMINAL_EVENT_AGENT_CONTENT", /* ROM 0x7662f0 */
    "TERMINAL_EVENT_QUERY", /* ROM 0x77c994 */
    "TERMINAL_EVENT_HEART_BEAT", /* ROM 0x7731b0 */
    "TERMINAL_EVENT_ERROR_MSG", /* ROM 0x7731cc */
    "TERMINAL_EVENT_SESSION_LIST", /* ROM 0x7731e8 */
    "TERMINAL_EVENT_SESSION_SWITCH_RESULT", /* ROM 0x74f5b4 */
    "TERMINAL_EVENT_NEW_SESSION_RESULT", /* ROM 0x75b4d8 */
    "TERMINAL_EVENT_SESSION_ID_CHANGED", /* ROM 0x75b4fc */
};

_Static_assert(sizeof audio_terminal_event_names == 52u,
               "terminal event-name pointer extent");
