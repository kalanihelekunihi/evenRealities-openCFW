/* Direct Apollo callback names for the validated power planner entries. */
#include "../platform_callbacks_offline/planner.c"

__asm__(".global callback_plan\n.set callback_plan, audio_platform_plan\n"
        ".global callback_change_state\n.set callback_change_state, audio_platform_change_state\n");
