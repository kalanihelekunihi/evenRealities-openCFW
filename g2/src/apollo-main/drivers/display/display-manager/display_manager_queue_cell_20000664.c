/* Apollo Main display-manager queue handle. Stock view at 0x474066 loads
 * RAM 0x20000658 + 0xc. Placement and runtime initialization need a
 * whole-image layout/startup check. */
#include <stdint.h>

/* Fix 59: this split copy was never written; users now read
 * audio_display_driver_manager+0xc (stock [0x20000658,#12], e.g. 0x474066 view). */
typedef int g2_display_manager_queue_cell_unit_nonempty;
