/* Stock Terminal RAM cluster at 0x2006e0d0, observed reset span 0x2a0. */
#include <stdint.h>

uint8_t audio_terminal_ui_state_base[0x2a0]
    __attribute__((section(".bss.opencfw.terminal.ui_state"),used,aligned(4)));

/* These separately named stock globals are fields in the same RAM block. */
__asm__(
    ".global audio_terminal_agent_session_ptr\n"
    ".set audio_terminal_agent_session_ptr,audio_terminal_ui_state_base+0x004\n"
    ".size audio_terminal_agent_session_ptr,4\n"
    ".global audio_terminal_mode_sync_pending\n"
    ".set audio_terminal_mode_sync_pending,audio_terminal_ui_state_base+0x274\n"
    ".size audio_terminal_mode_sync_pending,1\n"
    ".global audio_terminal_ui_mode\n"
    ".set audio_terminal_ui_mode,audio_terminal_ui_state_base+0x275\n"
    ".size audio_terminal_ui_mode,1\n"
    ".global audio_terminal_runtime_flag_277\n"
    ".set audio_terminal_runtime_flag_277,audio_terminal_ui_state_base+0x277\n"
    ".size audio_terminal_runtime_flag_277,1\n"
    ".global audio_terminal_selector_loading\n"
    ".set audio_terminal_selector_loading,audio_terminal_ui_state_base+0x27d\n"
    ".size audio_terminal_selector_loading,1\n"
    ".global audio_terminal_runtime_flag_27f\n"
    ".set audio_terminal_runtime_flag_27f,audio_terminal_ui_state_base+0x27f\n"
    ".size audio_terminal_runtime_flag_27f,1\n"
    ".global audio_terminal_runtime_saved_session\n"
    ".set audio_terminal_runtime_saved_session,audio_terminal_ui_state_base+0x288\n"
    ".size audio_terminal_runtime_saved_session,4\n"
    ".global audio_terminal_agent_special_flag\n"
    ".set audio_terminal_agent_special_flag,audio_terminal_ui_state_base+0x28c\n"
    ".size audio_terminal_agent_special_flag,1\n"
    ".global audio_terminal_output_tracking\n"
    ".set audio_terminal_output_tracking,audio_terminal_ui_state_base+0x294\n"
    ".size audio_terminal_output_tracking,8\n"
    ".global audio_terminal_session_switch_tick\n"
    ".set audio_terminal_session_switch_tick,audio_terminal_ui_state_base+0x29c\n"
    ".size audio_terminal_session_switch_tick,4\n"
);

_Static_assert(sizeof audio_terminal_ui_state_base==0x2a0u,"stock reset span");
