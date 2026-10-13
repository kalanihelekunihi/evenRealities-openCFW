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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-freetype-init-round364/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096


.global audio_uart_display_lv_state
.set audio_uart_display_lv_state,audio_uart_display_lv_root

.section .text.audio_uart_lv_heap_alloc,"ax"
.global audio_uart_lv_heap_alloc
.thumb_func
audio_uart_lv_heap_alloc: bx lr

.section .text.audio_uart_ft_init_freetype_52431c,"ax"
.global audio_uart_ft_init_freetype_52431c
.thumb_func
audio_uart_ft_init_freetype_52431c: bx lr

.section .text.audio_uart_lv_cache_create_4d4cd4,"ax"
.global audio_uart_lv_cache_create_4d4cd4
.thumb_func
audio_uart_lv_cache_create_4d4cd4: bx lr

.section .text.audio_uart_lvgl_log,"ax"
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr

.section .text.audio_uart_ft_node_compare_4b2342,"ax"
.global audio_uart_ft_node_compare_4b2342
.thumb_func
audio_uart_ft_node_compare_4b2342: bx lr

.section .text.audio_uart_ft_node_create_4b220a,"ax"
.global audio_uart_ft_node_create_4b220a
.thumb_func
audio_uart_ft_node_create_4b220a: bx lr

.section .text.audio_uart_ft_node_free_4b2308,"ax"
.global audio_uart_ft_node_free_4b2308
.thumb_func
audio_uart_ft_node_free_4b2308: bx lr

.section .rodata.fixture_class,"a"
.global audio_uart_font_cache_backend_vtable
audio_uart_font_cache_backend_vtable: .space 96
