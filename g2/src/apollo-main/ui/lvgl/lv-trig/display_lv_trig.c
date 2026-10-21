/* Native Main 0x4885f0, pinned LVGL 9.3 src/misc/lv_math.c sin0_90_table. */
#include <stdint.h>
static const uint16_t sin0_90_table[91] = {
    0,     572,   1144,  1715,  2286,  2856,  3425,  3993,  4560,  5126,  5690,  6252,  6813,  7371,  7927,  8481,
    9032,  9580,  10126, 10668, 11207, 11743, 12275, 12803, 13328, 13848, 14365, 14876, 15384, 15886, 16384, 16877,
    17364, 17847, 18324, 18795, 19261, 19720, 20174, 20622, 21063, 21498, 21926, 22348, 22763, 23170, 23571, 23965,
    24351, 24730, 25102, 25466, 25822, 26170, 26510, 26842, 27166, 27482, 27789, 28088, 28378, 28660, 28932, 29197,
    29452, 29698, 29935, 30163, 30382, 30592, 30792, 30983, 31164, 31336, 31499, 31651, 31795, 31928, 32052, 32166,
    32270, 32365, 32449, 32524, 32588, 32643, 32688, 32723, 32748, 32763, 32768
};
int32_t audio_uart_lv_sin_4885f0(int16_t angle) {
    while(angle<0)angle=(int16_t)(angle+360);
    while(angle>=360)angle=(int16_t)(angle-360);
    int32_t value;
    if(angle<90)value=sin0_90_table[angle];
    else if(angle<180)value=sin0_90_table[180-angle];
    else if(angle<270)value=-(int32_t)sin0_90_table[angle-180];
    else value=-(int32_t)sin0_90_table[360-angle];
    if(value==32767)return 32768;
    if(value==-32767)return -32768;
    return value;
}
