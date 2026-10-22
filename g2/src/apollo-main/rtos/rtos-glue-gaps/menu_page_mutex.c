/* Menu page data lock, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\menu\menu_page.c.
 * Native 0x460178..0x46018d (literal 0x46061c). Lazily creates the default
 * CMSIS mutex; called from Menu_common_data_handler (0x460638) and 0x46327e. */
#include <stdint.h>
#include <stddef.h>

extern void *g2_menu_page_mutex; /* RAM 0x200746e4 */
extern void *osMutexNew(const void *attr); /* 0x44971c */

void menu_page_mutex_init_460178(void)
{
    if (g2_menu_page_mutex == NULL)
        g2_menu_page_mutex = osMutexNew(NULL);
}
