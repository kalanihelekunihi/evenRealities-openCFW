.syntax unified
.thumb
.section .note.GNU-stack,"",%progbits
.section .vectors,"a"
.word 0x2007ff00
.word probe_stop
.rept 14
.word probe_stop
.endr
.section .reset,"ax"
.global probe_stop
.thumb_func
probe_stop: b .
.section .native_main,"ax"
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-refr-size-connected-round340/oracle-data-bound.bin"
.section .text.controlled_children,"ax"
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr
.global audio_uart_lv_obj_parent_44dca2
.thumb_func
audio_uart_lv_obj_parent_44dca2: bx lr
.global audio_uart_lv_obj_width_43fd9e
.thumb_func
audio_uart_lv_obj_width_43fd9e: bx lr
.global audio_uart_lv_obj_height_43fdda
.thumb_func
audio_uart_lv_obj_height_43fdda: bx lr
.global audio_uart_lv_obj_content_width_43fe16
.thumb_func
audio_uart_lv_obj_content_width_43fe16: bx lr
.global audio_uart_lv_obj_content_height_43fe70
.thumb_func
audio_uart_lv_obj_content_height_43fe70: bx lr
.global audio_uart_lv_style_property_44bdea
.thumb_func
audio_uart_lv_style_property_44bdea: bx lr
.global audio_uart_lv_child_count_44ddea
.thumb_func
audio_uart_lv_child_count_44ddea: bx lr
.global audio_uart_lv_obj_has_flag_any_43e11c
.thumb_func
audio_uart_lv_obj_has_flag_any_43e11c: bx lr
.global audio_uart_lv_obj_x_44e486
.thumb_func
audio_uart_lv_obj_x_44e486: bx lr
.global audio_uart_lv_obj_y_44e498
.thumb_func
audio_uart_lv_obj_y_44e498: bx lr
.global audio_uart_lv_obj_event_451670
.thumb_func
audio_uart_lv_obj_event_451670: bx lr
.global audio_uart_display_size_changed
.thumb_func
audio_uart_display_size_changed: bx lr
.global audio_uart_lv_area_contains_450f28
.thumb_func
audio_uart_lv_area_contains_450f28: bx lr
.global audio_uart_lv_refresh_draw_452d42
.thumb_func
audio_uart_lv_refresh_draw_452d42: bx lr
.global audio_uart_lv_obj_has_flag_43e0e0
.thumb_func
audio_uart_lv_obj_has_flag_43e0e0: bx lr
.global audio_uart_display_default_get
.thumb_func
audio_uart_display_default_get: bx lr
.section .bss.root,"aw",%nobits
.global audio_uart_display_lv_root
.balign 4
audio_uart_display_lv_root: .space 512

.section .text.controlled_children,"ax"
.global audio_uart_display_invalidate_area
.thumb_func
audio_uart_display_invalidate_area: bx lr

.section .text.controlled_children,"ax"
.global audio_uart_lv_area_width_451598
.thumb_func
audio_uart_lv_area_width_451598: bx lr

.section .text.controlled_children,"ax"
.global audio_uart_lv_area_height_4515a4
.thumb_func
audio_uart_lv_area_height_4515a4: bx lr
