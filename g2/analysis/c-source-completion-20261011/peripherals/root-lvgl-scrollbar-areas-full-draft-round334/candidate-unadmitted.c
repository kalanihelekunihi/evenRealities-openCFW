/* Entire native 44eb28..44f2c9 scrollbar area calculator.
 * Pinned Ambiq LVGL lv_obj_scroll.c461-635 reconciled with existing native lift.
 * Unadmitted: native comparison and selected-TU binding gates remain.
 * All signed arithmetic wraps explicitly; DPI reads retain native macro repeats. */
#include <stdint.h>
#include <limits.h>
extern void audio_uart_lv_area_set_450b5c(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *,uint32_t);
extern uint32_t audio_uart_lv_get_scrollbar_mode_44e42c(const void *);
extern void *audio_uart_lv_input_next_452edc(void *);
extern void *audio_uart_lv_input_scroll_object_452fae(const void *);
extern uint32_t audio_uart_lv_input_scroll_direction_452f8c(const void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *); /* native equivalent 44e4aa */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *);
extern int32_t audio_uart_lv_scroll_left_44e586(void *);
extern int32_t audio_uart_lv_scroll_right_44e67a(void *);
extern uint32_t audio_uart_lv_get_scroll_dir_44e442(const void *);
extern uint8_t audio_uart_lv_style_base_dir_43efba(void *,uint32_t);
extern int32_t audio_uart_lv_style_raw_pad_top_44e230(void *,uint32_t);
extern int32_t audio_uart_lv_style_raw_pad_bottom_44e23a(void *,uint32_t);
extern int32_t audio_uart_lv_style_raw_pad_left_44e244(void *,uint32_t);
extern int32_t audio_uart_lv_style_raw_pad_right_44e24e(void *,uint32_t);
extern int32_t audio_uart_lv_style_width_43eea6(void *,uint32_t);
extern int32_t audio_uart_lv_style_length_44e226(void *,uint32_t);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern uint8_t audio_uart_lv_style_background_opacity_44e276(void *,uint32_t);
extern uint8_t audio_uart_lv_style_border_opacity_44e282(void *,uint32_t);
extern int32_t audio_uart_lv_display_dpi_44fbe6(void *);

static int32_t lv334_add(int32_t a,int32_t b){return (int32_t)((uint32_t)a+(uint32_t)b);}
static int32_t lv334_sub(int32_t a,int32_t b){return (int32_t)((uint32_t)a-(uint32_t)b);}
static int32_t lv334_mul(int32_t a,int32_t b){return (int32_t)((uint32_t)a*(uint32_t)b);}
static int32_t lv334_div(int32_t a,int32_t b)
{
    if(b==0)return 0;
    if(a==INT32_MIN && b==-1)return INT32_MIN;
    return a/b;
}
static int32_t lv334_coord(const void *o,uint32_t offset)
{return *(const volatile int32_t *)((const uint8_t *)o+offset);}
static int32_t lv334_min_size(void)
{
    int32_t dpi=audio_uart_lv_display_dpi_44fbe6(0);
    int32_t scaled=lv334_div(lv334_add(lv334_mul(dpi,10),80),160);
    if(scaled<2)return 1;
    dpi=audio_uart_lv_display_dpi_44fbe6(0);
    return lv334_div(lv334_add(lv334_mul(dpi,10),80),160);
}
static int32_t lv334_length(int32_t calculated,int32_t style,int32_t extent)
{
    int32_t minimum=lv334_min_size();
    int32_t candidate=style>0?style:calculated;
    if(minimum<candidate){if(style>0)calculated=style;}
    else calculated=lv334_min_size();
    if(extent<=calculated)calculated=extent;
    return calculated;
}
void audio_uart_lv_get_scrollbar_areas_44eb28(void *object,int32_t *horizontal,int32_t *vertical)
{
    volatile int32_t *h=horizontal,*v=vertical;
    audio_uart_lv_area_set_450b5c(horizontal,0u,0u,UINT32_MAX,UINT32_MAX);
    audio_uart_lv_area_set_450b5c(vertical,0u,0u,UINT32_MAX,UINT32_MAX);
    if(audio_uart_lv_obj_has_flag_43e0e0(object,16u)==0u)return;
    uint32_t mode=audio_uart_lv_get_scrollbar_mode_44e42c(object);
    if(mode==0u)return;
    void *input=audio_uart_lv_input_next_452edc(0);
    if(mode==2u){
        while(input!=0 && audio_uart_lv_input_scroll_object_452fae(input)!=object)
            input=audio_uart_lv_input_next_452edc(input);
        if(input==0)return;
    }
    int32_t st=audio_uart_lv_obj_y_44e498(object);
    int32_t sb=audio_uart_lv_scroll_bottom_44e4bc(object);
    int32_t sl=audio_uart_lv_scroll_left_44e586(object);
    int32_t sr=audio_uart_lv_scroll_right_44e67a(object);
    uint32_t dir=audio_uart_lv_get_scroll_dir_44e442(object);
    uint32_t ver_draw=0u,hor_draw=0u;
    if((dir&12u)!=0u && (mode==1u || (mode==3u && (st>0 || sb>0)) ||
       (mode==2u && audio_uart_lv_input_scroll_direction_452f8c(input)==12u)))ver_draw=1u;
    if((dir&3u)!=0u && (mode==1u || (mode==3u && (sl>0 || sr>0)) ||
       (mode==2u && audio_uart_lv_input_scroll_direction_452f8c(input)==3u)))hor_draw=1u;
    if(hor_draw==0u && ver_draw==0u)return;
    uint32_t rtl=audio_uart_lv_style_base_dir_43efba(object,0x10000u)==1u;
    int32_t top=audio_uart_lv_style_raw_pad_top_44e230(object,0x10000u);
    int32_t bottom=audio_uart_lv_style_raw_pad_bottom_44e23a(object,0x10000u);
    int32_t left=audio_uart_lv_style_raw_pad_left_44e244(object,0x10000u);
    int32_t right=audio_uart_lv_style_raw_pad_right_44e24e(object,0x10000u);
    int32_t thickness=audio_uart_lv_style_width_43eea6(object,0x10000u);
    int32_t length=audio_uart_lv_style_length_44e226(object,0x10000u);
    int32_t obj_h=audio_uart_lv_obj_height_43fdda(object);
    int32_t obj_w=audio_uart_lv_obj_width_43fd9e(object);
    int32_t ver_req=ver_draw?thickness:0,hor_req=hor_draw?thickness:0;
    if(audio_uart_lv_style_background_opacity_44e276(object,0x10000u)<=1u &&
       audio_uart_lv_style_border_opacity_44e282(object,0x10000u)<=1u)return;
    int32_t content_h=lv334_add(lv334_add(sb,st),obj_h);
    if(ver_draw && content_h!=0){
        v[1]=lv334_coord(object,24);v[3]=lv334_coord(object,32);
        if(rtl){v[0]=lv334_add(left,lv334_coord(object,20));v[2]=lv334_sub(lv334_add(thickness,v[0]),1);}
        else{v[2]=lv334_sub(lv334_coord(object,28),right);v[0]=lv334_add(lv334_sub(v[2],thickness),1);}
        int32_t track=lv334_sub(lv334_sub(lv334_sub(obj_h,top),bottom),hor_req);
        int32_t sb_h=lv334_length(lv334_div(lv334_mul(obj_h,track),content_h),length,obj_h);
        int32_t rem=lv334_sub(track,sb_h),scroll_h=lv334_sub(content_h,obj_h);
        if(scroll_h<1){
            v[1]=lv334_add(top,lv334_coord(object,24));
            v[3]=lv334_sub(lv334_sub(lv334_sub(lv334_coord(object,32),bottom),hor_req),1);
        }else{
            int32_t y=lv334_sub(rem,lv334_div(lv334_mul(sb,rem),scroll_h));
            v[1]=lv334_add(lv334_add(top,y),lv334_coord(object,24));v[3]=lv334_sub(lv334_add(sb_h,v[1]),1);
            if(v[1]<lv334_add(top,lv334_coord(object,24))){
                v[1]=lv334_add(top,lv334_coord(object,24));int32_t minimum=lv334_min_size();
                if(v[3]<lv334_add(minimum,v[1])){minimum=lv334_min_size();v[3]=lv334_add(minimum,v[1]);}
            }
            if(lv334_sub(lv334_sub(lv334_coord(object,32),hor_req),bottom)<v[3]){
                v[3]=lv334_sub(lv334_sub(lv334_coord(object,32),hor_req),bottom);int32_t minimum=lv334_min_size();
                if(lv334_sub(v[3],minimum)<v[1]){minimum=lv334_min_size();v[1]=lv334_sub(v[3],minimum);}
            }
        }
    }
    int32_t content_w=lv334_add(lv334_add(sr,sl),obj_w);
    if(hor_draw && content_w!=0){
        h[3]=lv334_sub(lv334_coord(object,32),bottom);h[1]=lv334_add(lv334_sub(h[3],thickness),1);
        h[0]=lv334_coord(object,20);h[2]=lv334_coord(object,28);
        int32_t track=lv334_sub(lv334_sub(lv334_sub(obj_w,left),right),ver_req);
        int32_t sb_w=lv334_length(lv334_div(lv334_mul(obj_w,track),content_w),length,obj_w);
        int32_t rem=lv334_sub(track,sb_w),scroll_w=lv334_sub(content_w,obj_w);
        if(scroll_w<1){
            if(rtl){h[0]=lv334_sub(lv334_add(lv334_add(ver_req,left),lv334_coord(object,20)),1);h[2]=lv334_sub(lv334_coord(object,28),right);}
            else{h[0]=lv334_add(left,lv334_coord(object,20));h[2]=lv334_sub(lv334_sub(lv334_sub(lv334_coord(object,28),right),ver_req),1);}
        }else{
            int32_t x=lv334_sub(rem,lv334_div(lv334_mul(sr,rem),scroll_w));
            if(rtl){
                h[0]=lv334_add(lv334_add(lv334_add(ver_req,left),x),lv334_coord(object,20));h[2]=lv334_sub(lv334_add(sb_w,h[0]),1);
                if(h[0]<lv334_add(lv334_add(ver_req,left),lv334_coord(object,20))){
                    h[0]=lv334_add(lv334_add(ver_req,left),lv334_coord(object,20));int32_t minimum=lv334_min_size();
                    if(h[2]<lv334_add(minimum,h[0])){minimum=lv334_min_size();h[2]=lv334_add(minimum,h[0]);}
                }
                if(lv334_sub(lv334_coord(object,28),right)<h[2]){
                    h[2]=lv334_sub(lv334_coord(object,28),right);int32_t minimum=lv334_min_size();
                    if(lv334_sub(h[2],minimum)<h[0]){minimum=lv334_min_size();h[0]=lv334_sub(h[2],minimum);}
                }
            }else{
                h[0]=lv334_add(lv334_add(left,x),lv334_coord(object,20));h[2]=lv334_sub(lv334_add(sb_w,h[0]),1);
                if(h[0]<lv334_add(left,lv334_coord(object,20))){
                    h[0]=lv334_add(left,lv334_coord(object,20));int32_t minimum=lv334_min_size();
                    if(h[2]<lv334_add(minimum,h[0])){minimum=lv334_min_size();h[2]=lv334_add(minimum,h[0]);}
                }
                if(lv334_sub(lv334_sub(lv334_coord(object,28),ver_req),right)<h[2]){
                    h[2]=lv334_sub(lv334_sub(lv334_coord(object,28),ver_req),right);int32_t minimum=lv334_min_size();
                    if(lv334_sub(h[2],minimum)<h[0]){minimum=lv334_min_size();h[0]=lv334_sub(h[2],minimum);}
                }
            }
        }
    }
}
