/* Apollo terminal-data RAM cluster, native base 0x2010fd20. */
#include <stdint.h>

/* Native td reset at 0x5970f0 clears this entire 0xa1dc-byte region. */
uint8_t audio_td_state[0xa1dc];
