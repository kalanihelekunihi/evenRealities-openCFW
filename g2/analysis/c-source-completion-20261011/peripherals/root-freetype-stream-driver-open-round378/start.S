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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-stream-driver-open-round378/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096





.section .text.audio_uart_ft_stream_open_path_5675e8,"ax"
.global audio_uart_ft_stream_open_path_5675e8
.thumb_func
audio_uart_ft_stream_open_path_5675e8: bx lr

.section .text.audio_uart_ft_find_unicode_charmap_52594a,"ax"
.global audio_uart_ft_find_unicode_charmap_52594a
.thumb_func
audio_uart_ft_find_unicode_charmap_52594a: bx lr

.section .text.probe_alloc,"ax"
.global probe_alloc
.thumb_func
probe_alloc: bx lr

.section .text.probe_free,"ax"
.global probe_free
.thumb_func
probe_free: bx lr

.section .text.probe_init_face,"ax"
.global probe_init_face
.thumb_func
probe_init_face: bx lr

.section .text.probe_done_face,"ax"
.global probe_done_face
.thumb_func
probe_done_face: bx lr
