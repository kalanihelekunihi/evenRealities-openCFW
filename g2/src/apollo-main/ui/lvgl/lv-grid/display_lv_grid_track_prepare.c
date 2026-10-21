/* Native LVGL grid calc_cols 0x48cbf8 and calc_rows 0x48cdec. */
#include <stdint.h>
extern uint32_t audio_uart_lv_grid_col_descriptor_48c97c(void *);
extern uint32_t audio_uart_lv_grid_row_descriptor_48c986(void *);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern uint32_t audio_uart_lv_grid_col_48c990(void *);
extern uint32_t audio_uart_lv_grid_row_48c99a(void *);
extern uint32_t audio_uart_lv_grid_col_span_48c9a4(void *);
extern uint32_t audio_uart_lv_grid_row_span_48c9ae(void *);
extern uint32_t audio_uart_lv_grid_descriptor_count_48d4d0(const int32_t *);
extern int32_t audio_uart_lv_grid_weight_round_48ca18(int32_t,int32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_free(void *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern void *audio_uart_lv_child_get_44dce2(void *,int32_t);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_obj_content_width_43fe16(void *);
extern int32_t audio_uart_lv_obj_content_height_43fe70(void *);
extern int32_t audio_uart_lv_basic_horizontal_48c860(void *,uint32_t);
extern int32_t audio_uart_lv_basic_vertical_48c856(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);

static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\layouts\\grid\\lv_grid.c";
static const char col_function[]="calc_cols";
static const char row_function[]="calc_rows";
static const char no_col[]="No col descriptor found even on the parent";
static const char no_row[]="No row descriptor found even on the parent";
enum {GRID_CONTENT=0x1fffff9a,GRID_FR_START=0x1fffff9b,GRID_LAST=0x1fffffff};

static uintptr_t prepare(void *object,uint32_t *state,uint32_t is_row)
{
    const int32_t *descriptor=(const int32_t *)(uintptr_t)(is_row?
        audio_uart_lv_grid_row_descriptor_48c986(object):audio_uart_lv_grid_col_descriptor_48c97c(object));
    uint32_t copied=0;
    if(!descriptor){
        void *parent=audio_uart_lv_obj_parent_44dca2(object);
        const int32_t *base=(const int32_t *)(uintptr_t)(is_row?
            audio_uart_lv_grid_row_descriptor_48c986(parent):audio_uart_lv_grid_col_descriptor_48c97c(parent));
        if(!base){
            audio_uart_lvgl_log(2u,source,is_row?0x179u:0x11du,
                                  is_row?row_function:col_function);
            return (uintptr_t)(is_row?no_row:no_col);
        }
        uint32_t start=is_row?audio_uart_lv_grid_row_48c99a(object):audio_uart_lv_grid_col_48c990(object);
        uint32_t span=is_row?audio_uart_lv_grid_row_span_48c9ae(object):audio_uart_lv_grid_col_span_48c9a4(object);
        int32_t *copy=(int32_t *)audio_uart_lv_malloc((span+1u)*4u);
        (void)audio_uart_lv_grid_copy_454738(copy,base+start,span*4u);
        copy[span]=GRID_LAST;
        descriptor=copy;
        copied=1u;
    }
    int32_t content=is_row?0:audio_uart_lv_obj_content_width_43fe16(object);
    uint32_t count=audio_uart_lv_grid_descriptor_count_48d4d0(descriptor);
    state[is_row?5:4]=count;
    int32_t *positions=(int32_t *)audio_uart_lv_malloc(count*4u);
    int32_t *sizes=(int32_t *)audio_uart_lv_malloc(count*4u);
    state[is_row?1:0]=(uint32_t)(uintptr_t)positions;
    state[is_row?3:2]=(uint32_t)(uintptr_t)sizes;
    for(uint32_t i=0;i<count;i++){
        if(descriptor[i]!=GRID_CONTENT)continue;
        int32_t maximum=(int32_t)0xe0000001u;
        for(uint32_t j=0;j<audio_uart_lv_child_count_44ddea(object);j++){
            void *child=audio_uart_lv_child_get_44dce2(object,(int32_t)j);
            if(audio_uart_lv_obj_has_flag_any_43e11c(child,0x60001u))continue;
            uint32_t span=is_row?audio_uart_lv_grid_row_span_48c9ae(child):audio_uart_lv_grid_col_span_48c9a4(child);
            if(span!=1u)continue;
            uint32_t start=is_row?audio_uart_lv_grid_row_48c99a(child):audio_uart_lv_grid_col_48c990(child);
            if(start!=i)continue;
            int32_t size=is_row?audio_uart_lv_obj_height_43fdda(child):audio_uart_lv_obj_width_43fd9e(child);
            if(maximum<=size)
                maximum=is_row?audio_uart_lv_obj_height_43fdda(child):audio_uart_lv_obj_width_43fd9e(child);
        }
        sizes[i]=maximum<0?0:maximum;
    }
    int32_t fraction_weight=0,fixed=0;
    for(uint32_t i=0;i<count;i++){
        int32_t d=descriptor[i];
        if(d<GRID_FR_START){
            if(d==GRID_CONTENT)fixed=(int32_t)((uint32_t)fixed+(uint32_t)sizes[i]);
            else {sizes[i]=d;fixed=(int32_t)((uint32_t)fixed+(uint32_t)d);}
        }else fraction_weight=(int32_t)((uint32_t)fraction_weight+(uint32_t)d-(uint32_t)GRID_FR_START);
    }
    int32_t gap=is_row?audio_uart_lv_basic_vertical_48c856(object,0u):audio_uart_lv_basic_horizontal_48c860(object,0u);
    if(is_row)content=audio_uart_lv_obj_content_height_43fe70(object);
    int32_t remaining=(int32_t)((uint32_t)content-(uint32_t)(count-1u)*(uint32_t)gap-(uint32_t)fixed);
    if(remaining<0)remaining=0;
    for(uint32_t i=0;i<count && fraction_weight!=0;i++){
        int32_t d=descriptor[i];
        if(d<GRID_FR_START)continue;
        int32_t weight=d-GRID_FR_START;
        int32_t size=audio_uart_lv_grid_weight_round_48ca18(
            (int32_t)((uint32_t)weight*(uint32_t)remaining),fraction_weight);
        sizes[i]=size;
        fraction_weight-=weight;remaining-=size;
    }
    if(copied)audio_uart_lv_free((void *)descriptor);
    (void)positions;
    return is_row?0u:(uintptr_t)content;
}

uintptr_t audio_uart_lv_basic_prepare_b_48cbf8(void *object,void *state)
{return prepare(object,(uint32_t *)state,0u);}
/* The native row helper passes incoming R3 through in R0 on success. Its
 * selected two-argument caller ignores that return; the fourth ABI register
 * remains a live passthrough rather than a synthetic constant. */
uintptr_t audio_uart_lv_basic_prepare_a_48cdec(void *object,void *state,
                                                uint32_t unused_r2,uintptr_t passthrough_r3)
{(void)unused_r2;uintptr_t result=prepare(object,(uint32_t *)state,1u);
 return result==0u?passthrough_r3:result;}
