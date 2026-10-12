/* Native LV area rounded containment 0x450dd4. Rectangle corners are tested
 * in the stock order, with the radius clamped to half each dimension. */
#include <stdint.h>
extern int32_t audio_uart_lv_area_width_451598(const int32_t *);
extern int32_t audio_uart_lv_area_height_4515a4(const int32_t *);
extern uint32_t audio_uart_lv_corner_arc_45163c(const int32_t *,const int32_t *);

uint32_t audio_uart_lv_round_corner_450dd4(const int32_t *area,const int32_t *point,uint32_t raw_radius) {
    if(point[0]<area[0] || point[0]>area[2] || point[1]<area[1] || point[1]>area[3])return 0u;
    int32_t radius=(int32_t)raw_radius;
    if(radius<1)return 1u;
    int32_t half=audio_uart_lv_area_width_451598(area)/2;
    int32_t h=audio_uart_lv_area_height_4515a4(area)/2;
    if(half>=h)half=h;
    if(half<radius)radius=half;
    int32_t corner[4]={area[0],area[1],area[0]+radius,area[1]+radius};
    if(audio_uart_lv_round_corner_450dd4(corner,point,0u)!=0u) {
        corner[2]+=radius;corner[3]+=radius;
        return audio_uart_lv_corner_arc_45163c(corner,point);
    }
    corner[1]=area[3]-radius;corner[3]=area[3];
    if(audio_uart_lv_round_corner_450dd4(corner,point,0u)!=0u) {
        corner[2]+=radius;corner[1]-=radius;
        return audio_uart_lv_corner_arc_45163c(corner,point);
    }
    corner[0]=area[2]-radius;corner[2]=area[2];
    if(audio_uart_lv_round_corner_450dd4(corner,point,0u)!=0u) {
        corner[0]-=radius;corner[1]-=radius;
        return audio_uart_lv_corner_arc_45163c(corner,point);
    }
    corner[1]=area[1];corner[3]=area[1]+radius;
    if(audio_uart_lv_round_corner_450dd4(corner,point,0u)!=0u) {
        corner[0]-=radius;corner[3]+=radius;
        return audio_uart_lv_corner_arc_45163c(corner,point);
    }
    return 1u;
}
