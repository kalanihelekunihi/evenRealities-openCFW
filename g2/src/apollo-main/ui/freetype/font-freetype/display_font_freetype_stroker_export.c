/* Native FT_Stroker_GetBorderCounts0x5696d4, ExportBorder0x569716,
 * FT_StrokeBorder_GetCounts0x5686be, Export0x568728. */
#include <stdint.h>
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439be4 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static int32_t border_get_counts(void *border,uint32_t *points,
                                 uint32_t *contours) { /* 0x5686be */
    uint32_t count=word(border,0u),n_points=0u,n_contours=0u;
    const uint8_t *tags=(const uint8_t *)(uintptr_t)word(border,12u);
    uint32_t open=0u;
    for(uint32_t i=0;i<count;i++) {
        uint8_t tag=tags[i];
        if((tag&4u)!=0u) {
            if(open!=0u) {n_points=0u;n_contours=0u;break;}
            open=1u;
        } else if(open==0u) {n_points=0u;n_contours=0u;break;}
        if((tag&8u)!=0u) {open=0u;n_contours++;}
        n_points++;
    }
    if(open==0u) ((uint8_t *)border)[28u]=1u;
    else {n_points=0u;n_contours=0u;}
    *points=n_points;*contours=n_contours;
    return 0;
}
void audio_uart_font_stroker_get_counts(void *stroker,uint8_t side,
                                        uint32_t *points,uint32_t *contours) {
    uint32_t p=0u,c=0u;
    if(stroker!=0&&side<2u)
        (void)border_get_counts((uint8_t *)stroker+0x34u+(uint32_t)side*0x20u,&p,&c);
    if(points!=0) *points=p;
    if(contours!=0) *contours=c;
}
static void border_export(void *border,void *outline) { /* 0x568728 */
    uint32_t count=word(border,0u);
    uint32_t old_points=(uint16_t)*(int16_t *)(const void *)((const uint8_t *)outline+2u);
    if(count!=0u)
        audio_uart_checksum_copy((uint8_t *)(uintptr_t)word(outline,4u)+old_points*8u,
                                 (const void *)(uintptr_t)word(border,8u),count*8u);
    const uint8_t *source_tags=(const uint8_t *)(uintptr_t)word(border,12u);
    uint8_t *target_tags=(uint8_t *)(uintptr_t)word(outline,8u)+old_points;
    int32_t index=*(int16_t *)(void *)((uint8_t *)outline+2u);
    for(uint32_t i=0;i<count;i++) {
        uint8_t tag=source_tags[i];
        target_tags[i]=(tag&1u)!=0u?1u:((tag&2u)!=0u?2u:0u);
    }
    uint8_t *target_ends=(uint8_t *)(uintptr_t)word(outline,12u);
    int16_t *end=(int16_t *)(void *)(target_ends+(uint32_t)(uint16_t)*(int16_t *)outline*2u);
    for(uint32_t i=0;i<count;i++) {
        if((source_tags[i]&8u)!=0u) {
            *end++=(int16_t)index;
            uint16_t contours=*(uint16_t *)outline;
            *(uint16_t *)outline=(uint16_t)(contours+1u);
        }
        index++;
    }
    uint16_t points=*(uint16_t *)(void *)((uint8_t *)outline+2u);
    *(uint16_t *)(void *)((uint8_t *)outline+2u)=(uint16_t)(points+count);
}
void audio_uart_font_stroker_export(void *stroker,uint8_t side,void *outline) {
    if(stroker==0||outline==0||side>1u) return;
    void *border=(uint8_t *)stroker+0x34u+(uint32_t)side*0x20u;
    if(((uint8_t *)border)[28u]!=0u) border_export(border,outline);
}
