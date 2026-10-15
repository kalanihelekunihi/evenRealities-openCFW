/* Apollo semantic_terminal_session_status_name, native 0x5e82a4. */
#include <stdint.h>

static const char none[]="SESSION_STATUS_NONE";
static const char thinking[]="SESSION_STATUS_THINKING";
static const char await_user[]="SESSION_STATUS_AWAIT_USER";
static const char done[]="SESSION_STATUS_DONE";
static const char reset[]="SESSION_STATUS_RESET";
static const char sync_end[]="SESSION_STATUS_SYNC_END";
static const char unknown[]="SESSION_STATUS_UNKNOWN";

const char *audio_terminal_session_status_name(uint32_t status) {
    switch((uint8_t)status) {
    case 0:return none;
    case 1:return thinking;
    case 2:return await_user;
    case 3:return done;
    case 4:return reset;
    case 5:return sync_end;
    default:return unknown;
    }
}
