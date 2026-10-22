/* Navigation data lock, native 0x585ca4..0x585cb9 (literal 0x586394). Stock source is
 * app\gui\navigation\navigation_data_handler.c by link adjacency (not proven by a string).
 * Lazily creates the default CMSIS mutex; called from 0x545d18 (navigation UI) and
 * navigation_data_dispatch (0x5872f4). */
#include <stdint.h>
#include <stddef.h>

extern void *g2_navigation_mutex; /* RAM 0x2007471c */
extern void *osMutexNew(const void *attr); /* 0x44971c */

void navigation_mutex_init_585ca4(void)
{
    if (g2_navigation_mutex == NULL)
        g2_navigation_mutex = osMutexNew(NULL);
}
