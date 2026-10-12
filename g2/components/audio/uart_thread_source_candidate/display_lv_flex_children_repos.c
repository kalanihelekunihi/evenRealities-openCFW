/* Native LVGL flex children_repos 0x48c14e, pinned v9.3 layout algorithm. */
#include <stdint.h>
typedef struct {uint8_t main_place,cross_place,track_place,flags;} Flex;
typedef struct {int32_t cross_size,main_size,fix_main_size;uint32_t item_count;
                void *grow_dsc;uint32_t grow_count,flags;} Track;
typedef struct {void *item;int32_t min_size,max_size,final_size;uint32_t grow_value,flags;} Grow;
extern void *audio_uart_lv_child_get_44dce2(void *,int32_t);
extern void *audio_uart_lv_flex_next_item_48c770(void *,uint32_t,int32_t *);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern uint32_t audio_uart_lv_flex_grow_48b9fc(void *,uint32_t);
extern uint32_t audio_uart_lv_flex_base_dir_48b9c0(void *,uint32_t);
extern int32_t audio_uart_lv_obj_content_width_43fe16(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_area_width_451598(void *);
extern int32_t audio_uart_lv_area_height_4515a4(void *);
extern void audio_uart_lv_rect_set_width_450b6c(void *,int32_t);
extern void audio_uart_lv_rect_set_height_450b76(void *,int32_t);
extern int32_t audio_uart_lv_flex_width_start_48b996(void *,uint32_t);
extern int32_t audio_uart_lv_flex_width_end_48b9a0(void *,uint32_t);
extern int32_t audio_uart_lv_flex_height_start_48b982(void *,uint32_t);
extern int32_t audio_uart_lv_flex_height_end_48b98c(void *,uint32_t);
extern uint32_t audio_uart_lv_flex_x_ofs_48b946(void *,uint32_t);
extern uint32_t audio_uart_lv_flex_y_ofs_48b950(void *,uint32_t);
extern void audio_uart_lv_place_content_48c6d8(uint32_t,int32_t,int32_t,uint32_t,int32_t *,int32_t *);
extern void audio_uart_display_size_changed(void *);
extern void audio_uart_lv_flex_rect_copy_48b8f8(void *,void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *,uint32_t,void *);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern void audio_uart_lv_obj_move_children_44035e(void *,int32_t,int32_t,uint32_t);
extern _Noreturn void audio_uart_lv_flex_repos_alloc_failure(void);

static int32_t style_offset(uint32_t v,int32_t size)
{
    if((v&0x60000000u)==0x20000000u && (int32_t)(v&0x9fffffffu)<0x1fffffff){
        uint32_t n=v&0x9fffffffu;
        n=n<0x10000000u?n:0x0fffffffu-n;
        return (int32_t)(n*(uint32_t)size)/100;
    }
    return (int32_t)v;
}
static int32_t rect_size(void *o,uint32_t row)
{return row?audio_uart_lv_area_width_451598((uint8_t *)o+0x14u):audio_uart_lv_area_height_4515a4((uint8_t *)o+0x14u);}
static int32_t rect_cross(void *o,uint32_t row)
{return row?audio_uart_lv_area_height_4515a4((uint8_t *)o+0x14u):audio_uart_lv_area_width_451598((uint8_t *)o+0x14u);}
static int32_t style_main(void *o,uint32_t row)
{return row?audio_uart_lv_flex_width_start_48b996(o,0u):audio_uart_lv_flex_height_start_48b982(o,0u);}
static int32_t style_cross(void *o,uint32_t row)
{return row?audio_uart_lv_flex_height_start_48b982(o,0u):audio_uart_lv_flex_width_start_48b996(o,0u);}
static int32_t style_cross_end(void *o,uint32_t row)
{return row?audio_uart_lv_flex_height_end_48b98c(o,0u):audio_uart_lv_flex_width_end_48b9a0(o,0u);}
static int32_t style_main_end(void *o,uint32_t row)
{return row?audio_uart_lv_flex_width_end_48b9a0(o,0u):audio_uart_lv_flex_height_end_48b98c(o,0u);}

void audio_uart_lv_children_repos_48c14e(void *object,Flex *flex,int32_t first,int32_t end,
                                          int32_t abs_x,int32_t abs_y,int32_t max_main,
                                          int32_t item_gap,Track *track)
{
    uint32_t row=flex->flags&1u,reverse=(flex->flags&4u)!=0u;
    Grow *g=(Grow *)track->grow_dsc;
    uint32_t again=1u;
    while(again && track->grow_count){
        again=0u;
        int32_t weight=0,remaining=track->main_size-track->fix_main_size;
        for(uint32_t i=0;i<track->grow_count;i++){
            if(g[i].flags&1u)remaining-=g[i].final_size;
            else weight+=(int32_t)g[i].grow_value;
        }
        for(uint32_t i=0;i<track->grow_count;i++){
            if(g[i].flags&1u)continue;
            if(!weight)audio_uart_lv_flex_repos_alloc_failure();
            int32_t proposal=(int32_t)g[i].grow_value*(remaining/weight);
            int32_t size=proposal;
            if(size>=g[i].max_size)size=g[i].max_size;
            if(size<g[i].min_size)size=g[i].min_size;
            if(size!=proposal){g[i].flags|=1u;again=1u;}
            g[i].final_size=size;
            weight-=(int32_t)g[i].grow_value;remaining-=size;
        }
    }
    uint32_t rtl=audio_uart_lv_flex_base_dir_48b9c0(object,0u)==1u;
    int32_t main_pos=0,between=0;
    audio_uart_lv_place_content_48c6d8(flex->main_place,max_main,track->main_size,
                                         track->item_count,&main_pos,&between);
    if(row && rtl)main_pos+=audio_uart_lv_obj_content_width_43fe16(object);
    int32_t index=first;
    void *item=audio_uart_lv_child_get_44dce2(object,index);
    while(item && index!=end){
        if(audio_uart_lv_obj_has_flag_any_43e11c(item,0x60001u)){
            item=audio_uart_lv_flex_next_item_48c770(object,reverse,&index);continue;
        }
        uint32_t grow=audio_uart_lv_flex_grow_48b9fc(item,0u);
        if(grow){
            int32_t size=0;
            for(uint32_t i=0;i<track->grow_count;i++)if(g[i].item==item){size=g[i].final_size;break;}
            uint16_t *flags=(uint16_t *)((uint8_t *)item+0x2au);
            if(row){*flags|=0x800u;*flags&=(uint16_t)~0x400u;}
            else {*flags|=0x400u;*flags&=(uint16_t)~0x800u;}
            int32_t old=rect_size(item,row);
            if(size!=old){
                uint8_t old_rect[20];
                audio_uart_display_size_changed(item);
                audio_uart_lv_flex_rect_copy_48b8f8(old_rect,(uint8_t *)item+0x14u);
                if(row)audio_uart_lv_rect_set_width_450b6c((uint8_t *)item+0x14u,size);
                else audio_uart_lv_rect_set_height_450b76((uint8_t *)item+0x14u,size);
                (void)audio_uart_lv_obj_event_451670(item,0x31u,old_rect);
                (void)audio_uart_lv_obj_event_451670(audio_uart_lv_obj_parent_44dca2(item),0x2au,item);
                audio_uart_display_size_changed(item);
            }
        }else{
            uint16_t *flags=(uint16_t *)((uint8_t *)item+0x2au);
            *flags&=(uint16_t)~0xc00u;
        }
        int32_t cross;
        if(flex->cross_place==1u){
            cross=track->cross_size-rect_cross(item,row)-style_cross_end(item,row);
        }else if(flex->cross_place==2u){
            int32_t a=style_cross(item,row),b=style_cross_end(item,row);
            cross=(a-b)/2+(int32_t)(((uint32_t)(track->cross_size+1)&~1u)-(uint32_t)rect_cross(item,row))/2;
        }else cross=style_cross(item,row);
        if(row && rtl)main_pos-=rect_size(item,row);
        int32_t width=audio_uart_lv_obj_width_43fd9e(item);
        int32_t height=audio_uart_lv_obj_height_43fdda(item);
        int32_t xo=style_offset(audio_uart_lv_flex_x_ofs_48b946(item,0u),width);
        int32_t yo=style_offset(audio_uart_lv_flex_y_ofs_48b950(item,0u),height);
        int32_t x= row?main_pos+style_main(item,row)+xo:cross+xo;
        int32_t y= row?cross+yo:main_pos+style_main(item,row)+yo;
        x+=abs_x-*(int32_t *)((uint8_t *)item+0x14u);
        y+=abs_y-*(int32_t *)((uint8_t *)item+0x18u);
        if(x||y){
            audio_uart_display_size_changed(item);
            int32_t *r=(int32_t *)((uint8_t *)item+0x14u);
            r[0]+=x;r[2]+=x;r[1]+=y;r[3]+=y;
            audio_uart_display_size_changed(item);
            audio_uart_lv_obj_move_children_44035e(item,x,y,0u);
        }
        if(row && rtl)main_pos-=item_gap+between;
        else main_pos+=rect_size(item,row)+style_main(item,row)+style_main_end(item,row)+between+item_gap;
        item=audio_uart_lv_flex_next_item_48c770(object,reverse,&index);
    }
}
