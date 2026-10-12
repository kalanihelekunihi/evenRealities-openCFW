/* Native LVGL flex_update callback 0x48bae4, pinned LVGL v9.3 flow. */
#include <stdint.h>

typedef struct {
    uint8_t main_place,cross_place,track_place,flags;
} Flex;
typedef struct {
    int32_t cross_size,main_size,fix_main_size;
    uint32_t item_count;
    void *grow_dsc;
    uint32_t grow_count,flags;
} Track;
extern uint32_t audio_uart_lv_flex_flow_48b9cc(void *,uint32_t);
extern uint8_t audio_uart_lv_flex_main_place_48b9d8(void *,uint32_t);
extern uint8_t audio_uart_lv_flex_cross_place_48b9e4(void *,uint32_t);
extern uint8_t audio_uart_lv_flex_track_place_48b9f0(void *,uint32_t);
extern uint32_t audio_uart_lv_flex_base_dir_48b9c0(void *,uint32_t);
extern int32_t audio_uart_lv_flex_pad_column_48b96e(void *,uint32_t);
extern int32_t audio_uart_lv_flex_pad_row_48b978(void *,uint32_t);
extern int32_t audio_uart_lv_obj_content_width_43fe16(void *);
extern int32_t audio_uart_lv_obj_content_height_43fe70(void *);
extern int32_t audio_uart_lv_flex_space_top_48ba36(void *,uint32_t);
extern int32_t audio_uart_lv_flex_space_left_48ba08(void *,uint32_t);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern int32_t audio_uart_lv_flex_width_48b90a(void *,uint32_t);
extern int32_t audio_uart_lv_flex_height_48b928(void *,uint32_t);
extern int32_t audio_uart_lv_find_track_end_48be22(void *,Flex *,int32_t,int32_t,int32_t,Track *);
extern void audio_uart_lv_place_content_48c6d8(uint32_t,int32_t,int32_t,uint32_t,int32_t *,int32_t *);
extern void audio_uart_lv_children_repos_48c14e(void *,Flex *,int32_t,int32_t,int32_t,int32_t,int32_t,int32_t,Track *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lv_basic_invalidate_43f1a4(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *,uint32_t,void *);

static int32_t count_children(void *object)
{
    uint8_t *spec=*(uint8_t **)((uint8_t *)object+8u);
    return (int32_t)*(uint16_t *)(void *)(spec+0x30u);
}

void audio_uart_lv_theme_default_apply_48bae4(void *object)
{
    uint32_t flow=audio_uart_lv_flex_flow_48b9cc(object,0u);
    Flex flex={audio_uart_lv_flex_main_place_48b9d8(object,0u),
               audio_uart_lv_flex_cross_place_48b9e4(object,0u),
               audio_uart_lv_flex_track_place_48b9f0(object,0u),
               (uint8_t)(((flow&1u)^1u)|(((flow>>2u)&1u)<<1u)|(((flow>>3u)&1u)<<2u))};
    uint32_t rtl=audio_uart_lv_flex_base_dir_48b9c0(object,0u)==1u;
    uint32_t row=flex.flags&1u;
    int32_t item_gap=row?audio_uart_lv_flex_pad_column_48b96e(object,0u):audio_uart_lv_flex_pad_row_48b978(object,0u);
    int32_t track_gap=row?audio_uart_lv_flex_pad_row_48b978(object,0u):audio_uart_lv_flex_pad_column_48b96e(object,0u);
    int32_t max_main=row?audio_uart_lv_obj_content_width_43fe16(object):audio_uart_lv_obj_content_height_43fe70(object);
    int32_t abs_y=(int32_t)*(uint32_t *)((uint8_t *)object+0x18u)+audio_uart_lv_flex_space_top_48ba36(object,0u)-audio_uart_lv_obj_y_44e498(object);
    int32_t abs_x=(int32_t)*(uint32_t *)((uint8_t *)object+0x14u)+audio_uart_lv_flex_space_left_48ba08(object,0u)-audio_uart_lv_obj_x_44e486(object);
    int32_t *cross_pos=row?&abs_y:&abs_x;
    int32_t width=audio_uart_lv_flex_width_48b90a(object,0u);
    int32_t height=audio_uart_lv_flex_height_48b928(object,0u);
    uint8_t place=flex.track_place;
    uint16_t layout_bits=*(uint16_t *)((uint8_t *)object+0x2au);
    if((row && height==0x3fffffff && (((layout_bits&0x7ffu)>>10u)==0u)) ||
       (!row && width==0x3fffffff && (((layout_bits&0xfffu)>>11u)==0u))) place=0u;
    if(rtl && !row){if(place==0u)place=1u;else if(place==1u)place=0u;}
    int32_t total_cross=0,gap=0;
    uint32_t track_count=0;
    int32_t count=count_children(object);
    int32_t first=(flex.flags&4u)?count-1:0;
    if(place!=0u){
        while(first<count && first>=0){
            Track track;track.flags=0u;
            int32_t next=audio_uart_lv_find_track_end_48be22(object,&flex,first,max_main,item_gap,&track);
            total_cross+=track.cross_size+track_gap;
            track_count++;first=next;
        }
        if(track_count)total_cross-=track_gap;
        int32_t max_cross=row?audio_uart_lv_obj_content_height_43fe70(object):audio_uart_lv_obj_content_width_43fe16(object);
        audio_uart_lv_place_content_48c6d8(place,max_cross,total_cross,track_count,cross_pos,&gap);
    }
    first=(flex.flags&4u)?count-1:0;
    if(rtl && !row)*cross_pos+=total_cross;
    while(first<count && first>=0){
        Track track;track.flags=1u;
        int32_t next=audio_uart_lv_find_track_end_48be22(object,&flex,first,max_main,item_gap,&track);
        if(rtl && !row)*cross_pos-=track.cross_size;
        audio_uart_lv_children_repos_48c14e(object,&flex,first,next,abs_x,abs_y,max_main,item_gap,&track);
        audio_uart_lv_heap_free(track.grow_dsc);
        first=next;
        if(rtl && !row)*cross_pos-=gap+track_gap;
        else *cross_pos+=track.cross_size+gap+track_gap;
    }
    if(width==0x3fffffff || height==0x3fffffff)
        audio_uart_lv_basic_invalidate_43f1a4(object);
    (void)audio_uart_lv_obj_event_451670(object,0x33u,0);
}
