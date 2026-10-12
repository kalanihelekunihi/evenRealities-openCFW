/* Native LVGL 9.3 grid item renderer 0x48cfe0. The 32-byte grid state and
 * 16-byte region are the authenticated call ABIs of grid_update. */
#include <stdint.h>
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern int32_t audio_uart_lv_grid_col_span_48c9a4(void *);
extern int32_t audio_uart_lv_grid_row_span_48c9ae(void *);
extern int32_t audio_uart_lv_grid_col_48c990(void *);
extern int32_t audio_uart_lv_grid_row_48c99a(void *);
extern uint8_t audio_uart_lv_grid_x_align_48c9b8(void *);
extern uint8_t audio_uart_lv_grid_y_align_48c9c2(void *);
extern uint8_t audio_uart_lv_grid_base_dir_48c8a8(void *,uint32_t);
extern int32_t audio_uart_lv_area_width_451598(void *);
extern int32_t audio_uart_lv_area_height_4515a4(void *);
extern int32_t audio_uart_lv_grid_x_start_48c87e(void *,uint32_t);
extern int32_t audio_uart_lv_grid_x_end_48c888(void *,uint32_t);
extern int32_t audio_uart_lv_grid_y_start_48c86a(void *,uint32_t);
extern int32_t audio_uart_lv_grid_y_end_48c874(void *,uint32_t);
extern int32_t audio_uart_lv_grid_x_auto_size_48c9e0(void *);
extern int32_t audio_uart_lv_grid_y_auto_size_48c9fc(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void audio_uart_lv_grid_box_copy_48c7fc(void *,void *);
extern void audio_uart_display_size_changed(void *);
extern void audio_uart_lv_rect_set_width_450b6c(void *,int32_t);
extern void audio_uart_lv_rect_set_height_450b76(void *,int32_t);
extern uint32_t audio_uart_lv_obj_event_451670(void *,uint32_t,void *);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern uint32_t audio_uart_lv_grid_x_ofs_48c82e(void *,uint32_t);
extern uint32_t audio_uart_lv_grid_y_ofs_48c838(void *,uint32_t);
extern void audio_uart_lv_obj_move_children_44035e(void *,int32_t,int32_t,uint32_t);

static int32_t grid_style_offset(uint32_t v,int32_t size)
{
    if((v&0x60000000u)==0x20000000u && (int32_t)(v&0x9fffffffu)<0x1fffffff){
        uint32_t n=v&0x9fffffffu;
        n=n<0x10000000u?n:0x0fffffffu-n;
        return (int32_t)(n*(uint32_t)size)/100;
    }
    return (int32_t)v;
}

void audio_uart_lv_basic_item_48cfe0(void *item,const uint32_t *grid,const int32_t *region)
{
    if(audio_uart_lv_obj_has_flag_any_43e11c(item,0x60001u))return;
    int32_t cols=audio_uart_lv_grid_col_span_48c9a4(item);
    int32_t rows=audio_uart_lv_grid_row_span_48c9ae(item);
    if(cols==0 || rows==0)return;
    int32_t col=audio_uart_lv_grid_col_48c990(item);
    int32_t row=audio_uart_lv_grid_row_48c99a(item);
    uint8_t xa=audio_uart_lv_grid_x_align_48c9b8(item);
    uint8_t ya=audio_uart_lv_grid_y_align_48c9c2(item);
    const int32_t *x=(const int32_t *)(uintptr_t)grid[0],*y=(const int32_t *)(uintptr_t)grid[1];
    const int32_t *w=(const int32_t *)(uintptr_t)grid[2],*h=(const int32_t *)(uintptr_t)grid[3];
    int32_t cell_w=(w[col+cols-1]+x[col+cols-1])-x[col];
    int32_t cell_h=(h[row+rows-1]+y[row+rows-1])-y[row];
    if(audio_uart_lv_grid_base_dir_48c8a8(item,0u)==1u){
        if(xa==0u)xa=2u;else if(xa==2u)xa=0u;
    }
    int32_t desired_w=audio_uart_lv_area_width_451598((uint8_t *)item+0x14u);
    int32_t desired_h=audio_uart_lv_area_height_4515a4((uint8_t *)item+0x14u);
    int32_t px;
    if(xa==1u){px=(audio_uart_lv_grid_x_start_48c87e(item,0u)-audio_uart_lv_grid_x_end_48c888(item,0u))/2+
                    (cell_w-desired_w)/2+x[col];*(uint16_t *)((uint8_t *)item+0x2au)&=(uint16_t)~0x800u;}
    else if(xa==2u){px=cell_w+x[col]-audio_uart_lv_obj_width_43fd9e(item)-audio_uart_lv_grid_x_end_48c888(item,0u);
                     *(uint16_t *)((uint8_t *)item+0x2au)&=(uint16_t)~0x800u;}
    else {px=audio_uart_lv_grid_x_start_48c87e(item,0u)+x[col];
          *(uint16_t *)((uint8_t *)item+0x2au)&=(uint16_t)~0x800u;
          if(xa==3u){desired_w=cell_w-audio_uart_lv_grid_x_auto_size_48c9e0(item);
                       *(uint16_t *)((uint8_t *)item+0x2au)|=0x800u;}}
    int32_t py;
    if(ya==1u){py=(audio_uart_lv_grid_y_start_48c86a(item,0u)-audio_uart_lv_grid_y_end_48c874(item,0u))/2+
                    (cell_h-desired_h)/2+y[row];*(uint16_t *)((uint8_t *)item+0x2au)&=(uint16_t)~0x400u;}
    else if(ya==2u){py=cell_h+y[row]-audio_uart_lv_obj_height_43fdda(item)-audio_uart_lv_grid_y_end_48c874(item,0u);
                     *(uint16_t *)((uint8_t *)item+0x2au)&=(uint16_t)~0x400u;}
    else {py=audio_uart_lv_grid_y_start_48c86a(item,0u)+y[row];
          *(uint16_t *)((uint8_t *)item+0x2au)&=(uint16_t)~0x400u;
          if(ya==3u){desired_h=cell_h-audio_uart_lv_grid_y_auto_size_48c9fc(item);
                       *(uint16_t *)((uint8_t *)item+0x2au)|=0x400u;}}
    if(audio_uart_lv_obj_width_43fd9e(item)!=desired_w || audio_uart_lv_obj_height_43fdda(item)!=desired_h){
        uint8_t old[16];audio_uart_lv_grid_box_copy_48c7fc(old,(uint8_t *)item+0x14u);
        audio_uart_display_size_changed(item);
        audio_uart_lv_rect_set_width_450b6c((uint8_t *)item+0x14u,desired_w);
        audio_uart_lv_rect_set_height_450b76((uint8_t *)item+0x14u,desired_h);
        audio_uart_display_size_changed(item);
        (void)audio_uart_lv_obj_event_451670(item,0x31u,old);
        (void)audio_uart_lv_obj_event_451670(audio_uart_lv_obj_parent_44dca2(item),0x2au,item);
    }
    int32_t xo=grid_style_offset(audio_uart_lv_grid_x_ofs_48c82e(item,0u),audio_uart_lv_obj_width_43fd9e(item));
    int32_t yo=grid_style_offset(audio_uart_lv_grid_y_ofs_48c838(item,0u),audio_uart_lv_obj_height_43fdda(item));
    int32_t dx=xo+px+region[2]-*(int32_t *)((uint8_t *)item+0x14u);
    int32_t dy=yo+py+region[3]-*(int32_t *)((uint8_t *)item+0x18u);
    if(dx || dy){
        audio_uart_display_size_changed(item);
        int32_t *r=(int32_t *)((uint8_t *)item+0x14u);
        r[0]+=dx;r[2]+=dx;r[1]+=dy;r[3]+=dy;
        audio_uart_display_size_changed(item);
        audio_uart_lv_obj_move_children_44035e(item,dx,dy,0u);
    }
}
