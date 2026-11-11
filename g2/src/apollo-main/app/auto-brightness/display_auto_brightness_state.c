/* Apollo MAIN s200 v2.2.6.10 auto-brightness cells within the authenticated
 * zero-initializer range 0x20004558..0x20075047. Absolute RAM placement
 * remains a linker contract. */
#include <stdint.h>

/* Fix 58: the two cells were split copies; they are audio_settings_config_live
 * +2/+4 (stock 0x46c164 strb [0x20072da8,#2], 0x46c17e str [#4]) and are
 * now accessed there by display_auto_brightness{,_configure}.c. */
typedef int g2_auto_brightness_state_unit_nonempty;
