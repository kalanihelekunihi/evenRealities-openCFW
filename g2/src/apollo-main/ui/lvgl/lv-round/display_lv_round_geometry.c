/* Native rectangle extent 0x451598/0x4515a4 and circle predicate 0x45163c. */
#include <stdint.h>
uint32_t audio_uart_lv_corner_arc_45163c(const int32_t *a,const int32_t *point) {
    int32_t radius=(int32_t)((uint32_t)a[2]-(uint32_t)a[0])/2;
    int32_t cx=(int32_t)((uint32_t)a[0]+(uint32_t)radius);
    int32_t cy=(int32_t)((uint32_t)a[1]+(uint32_t)radius);
    uint32_t dx=(uint32_t)point[0]-(uint32_t)cx;
    uint32_t dy=(uint32_t)point[1]-(uint32_t)cy;
    uint32_t square=(uint32_t)radius*(uint32_t)radius;
    uint32_t distance=dx*dx+dy*dy;
    return square>=distance ? 1u:0u;
}
