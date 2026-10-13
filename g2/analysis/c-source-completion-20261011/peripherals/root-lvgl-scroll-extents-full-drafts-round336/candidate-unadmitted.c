/* Entire native scroll-bottom44e4bc..44e585, left44e586..44e679,
 * right44e67a..44e75d. Pinned Ambiq LVGL lv_obj_scroll.c136-242.
 * Unadmitted: complete native/selected-TU/compiler qualification remains.
 * Native null assertions retain genuine faulting stores, not substitute traps. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_bottom_43ef7a(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_left_43ef84(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_right_43ef8e(void *,uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_bottom_43f050(void *,uint32_t);
extern int32_t audio_uart_lv_style_pad_left_43efc6(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_right_43eff4(void *,uint32_t);
extern uint8_t audio_uart_lv_style_base_dir_43efba(void *,uint32_t);
extern int32_t audio_uart_lv_self_height_43ff5e(void *);
extern int32_t audio_uart_lv_self_width_43ff44(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
static int32_t lv336_add(int32_t a,int32_t b){return (int32_t)((uint32_t)a+(uint32_t)b);}
static int32_t lv336_sub(int32_t a,int32_t b){return (int32_t)((uint32_t)a-(uint32_t)b);}
static uint32_t lv336_word(const void *p,uint32_t offset)
{return *(const volatile uint32_t *)((const uint8_t *)p+offset);}
static void *lv336_child(void *object,uint32_t index)
{
    void *spec=(void *)(uintptr_t)lv336_word(object,8u);
    void *children=(void *)(uintptr_t)lv336_word(spec,0u);
    return (void *)(uintptr_t)lv336_word(children,index*4u);
}
static _Noreturn void lv336_null(uint32_t line,const char *function)
{
    audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_scroll.c",
        line,function,"Asserted at expression: %s (%s)","obj != NULL","NULL pointer");
    for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
int32_t audio_uart_lv_scroll_bottom_44e4bc(void *object)
{
    if(object==0)lv336_null(138u,"lv_obj_get_scroll_bottom");
    const int32_t minimum=(int32_t)0xe0000001u;
    int32_t child_res=minimum;uint32_t count=audio_uart_lv_child_count_44ddea(object);
    for(uint32_t i=0;i<count;i++){
        void *child=lv336_child(object,i);
        if(audio_uart_lv_obj_has_flag_any_43e11c(child,0x40001u))continue;
        int32_t margin=audio_uart_lv_style_margin_bottom_43ef7a(child,0u);
        int32_t tmp=lv336_add(margin,(int32_t)lv336_word(child,32u));
        if(child_res<=tmp)child_res=tmp;
    }
    int32_t top=audio_uart_lv_style_pad_top_43f022(object,0u,0u,0u);
    int32_t bottom=audio_uart_lv_style_pad_bottom_43f050(object,0u);
    if(child_res!=minimum)child_res=lv336_add(bottom,lv336_sub(child_res,(int32_t)lv336_word(object,32u)));
    int32_t self=audio_uart_lv_self_height_43ff5e(object);
    int32_t height=audio_uart_lv_obj_height_43fdda(object);
    self=lv336_add(bottom,lv336_add(top,lv336_sub(self,height)));
    int32_t scroll=audio_uart_lv_obj_y_44e498(object);self=lv336_sub(self,scroll);
    return self>=child_res?self:child_res;
}
int32_t audio_uart_lv_scroll_left_44e586(void *object)
{
    if(object==0)lv336_null(166u,"lv_obj_get_scroll_left");
    if(audio_uart_lv_style_base_dir_43efba(object,0u)!=1u){
        void *spec=(void *)(uintptr_t)lv336_word(object,8u);
        return spec==0?0:(int32_t)(0u-lv336_word(spec,32u));
    }
    int32_t right=audio_uart_lv_style_pad_right_43eff4(object,0u);
    int32_t left=audio_uart_lv_style_pad_left_43efc6(object,0u,0u,0u);
    int32_t x1=0x1fffffff;uint32_t count=audio_uart_lv_child_count_44ddea(object);
    for(uint32_t i=0;i<count;i++){
        void *child=lv336_child(object,i);
        if(audio_uart_lv_obj_has_flag_any_43e11c(child,0x40001u))continue;
        int32_t margin=audio_uart_lv_style_margin_left_43ef84(child,0u);
        int32_t tmp=lv336_sub((int32_t)lv336_word(child,20u),margin);
        if(tmp<=x1)x1=tmp;
    }
    int32_t child_res=(int32_t)0xe0000001u;
    if(x1!=0x1fffffff)child_res=lv336_sub(lv336_add(left,(int32_t)lv336_word(object,20u)),x1);
    int32_t self=audio_uart_lv_self_width_43ff44(object);
    int32_t width=audio_uart_lv_obj_width_43fd9e(object);
    self=lv336_add(right,lv336_add(left,lv336_sub(self,width)));
    int32_t scroll=audio_uart_lv_obj_x_44e486(object);self=lv336_add(scroll,self);
    return self>=child_res?self:child_res;
}
int32_t audio_uart_lv_scroll_right_44e67a(void *object)
{
    if(object==0)lv336_null(209u,"lv_obj_get_scroll_right");
    if(audio_uart_lv_style_base_dir_43efba(object,0u)==1u){
        void *spec=(void *)(uintptr_t)lv336_word(object,8u);
        return spec==0?0:(int32_t)lv336_word(spec,32u);
    }
    const int32_t minimum=(int32_t)0xe0000001u;
    int32_t child_res=minimum;uint32_t count=audio_uart_lv_child_count_44ddea(object);
    for(uint32_t i=0;i<count;i++){
        void *child=lv336_child(object,i);
        if(audio_uart_lv_obj_has_flag_any_43e11c(child,0x40001u))continue;
        int32_t margin=audio_uart_lv_style_margin_right_43ef8e(child,0u);
        int32_t tmp=lv336_add(margin,(int32_t)lv336_word(child,28u));
        if(child_res<=tmp)child_res=tmp;
    }
    int32_t right=audio_uart_lv_style_pad_right_43eff4(object,0u);
    int32_t left=audio_uart_lv_style_pad_left_43efc6(object,0u,0u,0u);
    if(child_res!=minimum)child_res=lv336_add(right,lv336_sub(child_res,(int32_t)lv336_word(object,28u)));
    int32_t self=audio_uart_lv_self_width_43ff44(object);
    int32_t width=audio_uart_lv_obj_width_43fd9e(object);
    self=lv336_add(left,lv336_add(right,lv336_sub(self,width)));
    int32_t scroll=audio_uart_lv_obj_x_44e486(object);self=lv336_sub(self,scroll);
    return self>=child_res?self:child_res;
}
