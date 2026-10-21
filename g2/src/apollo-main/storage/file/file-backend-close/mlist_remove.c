/* LittleFS open-list unlink, stock 0x4cb0a0. */
#include <stdint.h>
struct g2_lfs_mlist { struct g2_lfs_mlist *next; };
void g2_lfs_mlist_remove(void *filesystem,void *node) {
    struct g2_lfs_mlist **p=(struct g2_lfs_mlist **)
        ((uint8_t *)filesystem+0x28u);
    while(*p) {
        if(*p==node) {
            *p=(*p)->next;
            return;
        }
        p=&(*p)->next;
    }
}
