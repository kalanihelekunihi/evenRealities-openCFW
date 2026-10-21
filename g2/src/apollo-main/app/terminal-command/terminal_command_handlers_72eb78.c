/* Apollo terminal_machine_handler callbacks at native ROM 0x72eb78.
 * Function pointers are relocations; final ROM placement is separate. */
#include <stdint.h>

typedef uint32_t (*audio_terminal_command_handler)(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e8846(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e8c48(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e8e6c(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9064(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9390(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9900(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9ab8(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9b08(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9c78(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9e62(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9ec8(const void *,uint32_t);
extern uint32_t audio_terminal_command_5e9f74(const void *,uint32_t);

const audio_terminal_command_handler audio_terminal_command_handlers[13]={
    0,
    audio_terminal_command_5e8846,
    audio_terminal_command_5e8c48,
    audio_terminal_command_5e8e6c,
    audio_terminal_command_5e9064,
    audio_terminal_command_5e9390,
    audio_terminal_command_5e9900,
    audio_terminal_command_5e9ab8,
    audio_terminal_command_5e9b08,
    audio_terminal_command_5e9c78,
    audio_terminal_command_5e9e62,
    audio_terminal_command_5e9ec8,
    audio_terminal_command_5e9f74,
};
