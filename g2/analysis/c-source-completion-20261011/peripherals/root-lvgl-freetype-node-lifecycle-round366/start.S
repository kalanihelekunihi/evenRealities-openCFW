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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-freetype-node-lifecycle-round366/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096


.global audio_uart_display_lv_state
.set audio_uart_display_lv_state,audio_uart_display_lv_root


.section .text.audio_uart_ft_new_face_525ade,"ax"
.global audio_uart_ft_new_face_525ade
.thumb_func
audio_uart_ft_new_face_525ade: bx lr

.section .text.audio_uart_ft_italic_transform_4b1fd4,"ax"
.global audio_uart_ft_italic_transform_4b1fd4
.thumb_func
audio_uart_ft_italic_transform_4b1fd4: bx lr

.section .text.audio_uart_lv_async_init_4d465c,"ax"
.global audio_uart_lv_async_init_4d465c
.thumb_func
audio_uart_lv_async_init_4d465c: bx lr

.section .text.audio_uart_ft_done_face_526814,"ax"
.global audio_uart_ft_done_face_526814
.thumb_func
audio_uart_ft_done_face_526814: bx lr

.section .text.audio_uart_lv_cache_destroy_4d4d6a,"ax"
.global audio_uart_lv_cache_destroy_4d4d6a
.thumb_func
audio_uart_lv_cache_destroy_4d4d6a: bx lr

.section .text.audio_queue_delete,"ax"
.global audio_queue_delete
.thumb_func
audio_queue_delete: bx lr

.section .text.audio_uart_lvgl_log,"ax"
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr
