/* Native 0x450f28 area containment; optional rounded-corner predicate is
 * the authentic 0x450dd4 child, called for all four corners in native order. */
#include <stdint.h>
extern uint32_t audio_uart_lv_round_corner_450dd4(const int32_t *,const int32_t *,uint32_t);

uint32_t audio_uart_lv_area_contains_450f28(const int32_t *inner,const int32_t *outer,uint32_t radius) {
    if(inner[0]<outer[0] || inner[1]<outer[1] || inner[2]>outer[2] || inner[3]>outer[3])return 0u;
    if(radius==0u)return 1u;
    int32_t corner[2];
    corner[0]=inner[0];corner[1]=inner[1];
    if(audio_uart_lv_round_corner_450dd4(outer,corner,radius)==0u)return 0u;
    corner[0]=inner[2];corner[1]=inner[1];
    if(audio_uart_lv_round_corner_450dd4(outer,corner,radius)==0u)return 0u;
    corner[0]=inner[0];corner[1]=inner[3];
    if(audio_uart_lv_round_corner_450dd4(outer,corner,radius)==0u)return 0u;
    corner[0]=inner[2];corner[1]=inner[3];
    return (uint8_t)audio_uart_lv_round_corner_450dd4(outer,corner,radius);
}
