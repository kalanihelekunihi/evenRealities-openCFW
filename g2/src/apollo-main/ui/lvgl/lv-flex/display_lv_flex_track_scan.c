/* Native LVGL flex find_track_end 0x48be22, pinned LVGL v9.3 track scan. */
#include <stdint.h>
typedef struct {uint8_t main_place,cross_place,track_place,flags;} Flex;
typedef struct {int32_t cross_size,main_size,fix_main_size;uint32_t item_count;
                void *grow_dsc;uint32_t grow_count,flags;} Track;
typedef struct {void *item;int32_t min_size,max_size,final_size;uint32_t grow_value,flags;} Grow;
extern int32_t audio_uart_lv_flex_width_48b90a(void *,uint32_t);
extern int32_t audio_uart_lv_flex_height_48b928(void *,uint32_t);
extern void *audio_uart_lv_child_get_44dce2(void *,int32_t);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *,uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern uint32_t audio_uart_lv_flex_grow_48b9fc(void *,uint32_t);
extern int32_t audio_uart_lv_flex_min_width_48b914(void *,uint32_t);
extern int32_t audio_uart_lv_flex_min_height_48b91e(void *,uint32_t);
extern int32_t audio_uart_lv_flex_max_width_48b932(void *,uint32_t);
extern int32_t audio_uart_lv_flex_max_height_48b93c(void *,uint32_t);
extern int32_t audio_uart_lv_flex_width_margin_48c7b4(void *);
extern int32_t audio_uart_lv_flex_height_margin_48c7d8(void *);
extern void *audio_uart_lv_realloc_44f76a(void *,uint32_t);
extern _Noreturn void audio_uart_lv_flex_grow_alloc_failure(void); /* stock in-body fatal path */
extern void *audio_uart_lv_flex_next_item_48c770(void *,uint32_t,int32_t *);

int32_t audio_uart_lv_find_track_end_48be22(void *object,Flex *flex,int32_t start,
                                               int32_t max_main,int32_t item_gap,Track *track)
{
    int32_t width=audio_uart_lv_flex_width_48b90a(object,0u);
    int32_t height=audio_uart_lv_flex_height_48b928(object,0u);
    uint32_t row=flex->flags&1u;
    if((flex->flags&2u) && ((row && width==0x3fffffff) || (!row && height==0x3fffffff)))
        flex->flags&=(uint8_t)~2u;
    track->cross_size=0;track->main_size=0;track->fix_main_size=0;
    track->item_count=0;track->grow_dsc=0;track->grow_count=0;
    int32_t id=start,grow_min_sum=0;
    void *item=audio_uart_lv_child_get_44dce2(object,id);
    uint32_t first=1u;
    while(item){
        if(id!=start && audio_uart_lv_obj_has_flag_43e0e0(item,0x200000u))break;
        if(!audio_uart_lv_obj_has_flag_any_43e11c(item,0x60001u)){
            uint32_t grow=(uint8_t)audio_uart_lv_flex_grow_48b9fc(item,0u);
            if(grow){
                int32_t min=row?audio_uart_lv_flex_min_width_48b914(item,0u):audio_uart_lv_flex_min_height_48b91e(item,0u);
                int32_t req=min+(id!=start?item_gap:0);
                if((flex->flags&2u) && track->fix_main_size+grow_min_sum+req>max_main)break;
                grow_min_sum+=req;
                if(id!=start)track->fix_main_size+=item_gap;
                track->grow_count++;
                if(track->flags&1u){
                    Grow *next=(Grow *)audio_uart_lv_realloc_44f76a(track->grow_dsc,24u*track->grow_count);
                    if(!next)audio_uart_lv_flex_grow_alloc_failure();
                    Grow *entry=&next[track->grow_count-1u];
                    entry->item=item;entry->min_size=row?audio_uart_lv_flex_min_width_48b914(item,0u):audio_uart_lv_flex_min_height_48b91e(item,0u);
                    entry->max_size=row?audio_uart_lv_flex_max_width_48b932(item,0u):audio_uart_lv_flex_max_height_48b93c(item,0u);
                    entry->grow_value=grow;entry->flags=0u;track->grow_dsc=next;
                }
            }else{
                int32_t size=row?audio_uart_lv_flex_width_margin_48c7b4(item):audio_uart_lv_flex_height_margin_48c7d8(item);
                int32_t req=size+(first?0:item_gap);
                if((flex->flags&2u) && track->fix_main_size+grow_min_sum+req>max_main)break;
                track->fix_main_size+=req;
            }
            first=0u;
            int32_t cross=row?audio_uart_lv_flex_height_margin_48c7d8(item):audio_uart_lv_flex_width_margin_48c7b4(item);
            /* LV_MAX macro evaluates the winning cross getter a second time. */
            if(cross>track->cross_size)
                track->cross_size=row?audio_uart_lv_flex_height_margin_48c7d8(item):audio_uart_lv_flex_width_margin_48c7b4(item);
            track->item_count++;
        }
        id+=(flex->flags&4u)?-1:1;
        if(id<0)break;
        item=audio_uart_lv_child_get_44dce2(object,id);
    }
    track->main_size=track->grow_count?max_main:track->fix_main_size;
    if(item && id==start){
        uint8_t *spec=*(uint8_t **)((uint8_t *)object+8u);
        uint32_t *items=*(uint32_t **)(void *)spec;
        item=(void *)(uintptr_t)items[id];
        (void)audio_uart_lv_flex_next_item_48c770(object,(flex->flags&4u)!=0u,&id);
        if(id>=0 && id<(int32_t)*(uint16_t *)(void *)(spec+0x30u)){
            track->cross_size=row?audio_uart_lv_flex_height_margin_48c7d8(item):audio_uart_lv_flex_width_margin_48c7b4(item);
            track->main_size=row?audio_uart_lv_flex_width_margin_48c7b4(item):audio_uart_lv_flex_height_margin_48c7d8(item);
            track->item_count=1u;
        }
    }
    return id;
}
