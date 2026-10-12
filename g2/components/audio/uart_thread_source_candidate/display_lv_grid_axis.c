/* Native LVGL grid axis placement 0x48d3c8, pinned v9.3 algorithm. */
#include <stdint.h>
int32_t audio_uart_lv_basic_axis_48d3c8(int32_t available,uint32_t auto_size,
                                         uint32_t placement,int32_t gap,uint32_t count,
                                         const int32_t *sizes,int32_t *positions,
                                         uint32_t reverse)
{
    uint8_t mode=(uint8_t)placement;
    if(!(uint8_t)auto_size){
        if(mode>=4u && mode<=6u){
            gap=0;
            if(count==1u)mode=1u;
        }
        int32_t used=0;
        for(uint32_t i=0;i<count;i++)
            used=(int32_t)((uint32_t)used+(uint32_t)gap+(uint32_t)sizes[i]);
        used=(int32_t)((uint32_t)used-(uint32_t)gap);
        if(mode==0u)positions[0]=0;
        else if(mode==1u)positions[0]=(available-used)/2;
        else if(mode==2u)positions[0]=available-used;
        else if(mode==4u){gap=(available-used)/(int32_t)(count+1u);positions[0]=gap;}
        else if(mode==5u){gap=(available-used)/(int32_t)count;positions[0]=gap/2;}
        else if(mode==6u){positions[0]=0;gap=(available-used)/(int32_t)(count-1u);}
    }else positions[0]=0;
    for(uint32_t i=0;i<count-1u;i++)
        positions[i+1u]=(int32_t)((uint32_t)gap+(uint32_t)sizes[i]+(uint32_t)positions[i]);
    int32_t extent=(int32_t)((uint32_t)sizes[count-1u]+(uint32_t)positions[count-1u]-(uint32_t)positions[0]);
    if((uint8_t)reverse){
        for(uint32_t i=0;i<count;i++)
            positions[i]=(int32_t)((uint32_t)available-(uint32_t)positions[i]-(uint32_t)sizes[i]);
    }
    return extent;
}
