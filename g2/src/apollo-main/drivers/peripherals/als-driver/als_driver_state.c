/* ALS driver state, stock D:\01_workspace\s200_ap510b_iar_git\driver\sensor\als\als.c.
 *
 * Cells referenced by the als.c literal pools 0x4ae3b4..0x4aea24 that no
 * other unit owns. All lie in the authenticated zero-initializer range
 * 0x20004558..0x20075047; final address placement is a linker contract and is
 * not established by this relocatable file. The shared ROM strings used by
 * every als.c log site are defined here once. */
#include <stdint.h>
#include "g2_als.h"
#include "als_log.h"

uint32_t g2_als_process_status;      /* 0x200741c4 */
uint32_t g2_als_dark_window_index;   /* 0x200741d0 */
uint32_t g2_als_dark_window_count;   /* 0x200741d4 */
uint32_t g2_als_dark_window[20];     /* 0x20072948..0x20072997 */
uint32_t g2_als_extreme_dark_active; /* 0x200741d8 */
g2_opt3007_regmap_t g2_als_opt3007_regmap; /* 0x20073134..0x2007316c */

const char g2_als_log_module[] = "sensor_als"; /* ROM 0x789f8c */
const char g2_als_log_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\sensor\\als\\als.c"; /* ROM 0x711ce0 */
