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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-open-face-round377/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096





.section .text.audio_uart_ft_stream_new_524f96,"ax"
.global audio_uart_ft_stream_new_524f96
.thumb_func
audio_uart_ft_stream_new_524f96: bx lr

.section .text.audio_uart_ft_open_driver_face_5259be,"ax"
.global audio_uart_ft_open_driver_face_5259be
.thumb_func
audio_uart_ft_open_driver_face_5259be: bx lr

.section .text.audio_uart_ft_list_add_529304,"ax"
.global audio_uart_ft_list_add_529304
.thumb_func
audio_uart_ft_list_add_529304: bx lr

.section .text.audio_uart_ft_new_glyph_slot_525386,"ax"
.global audio_uart_ft_new_glyph_slot_525386
.thumb_func
audio_uart_ft_new_glyph_slot_525386: bx lr

.section .text.audio_uart_ft_new_size_52687e,"ax"
.global audio_uart_ft_new_size_52687e
.thumb_func
audio_uart_ft_new_size_52687e: bx lr

.section .text.audio_uart_ft_stream_seek_5288e0,"ax"
.global audio_uart_ft_stream_seek_5288e0
.thumb_func
audio_uart_ft_stream_seek_5288e0: bx lr

.section .text.audio_uart_ft_open_ps_sfnt_525d32,"ax"
.global audio_uart_ft_open_ps_sfnt_525d32
.thumb_func
audio_uart_ft_open_ps_sfnt_525d32: bx lr

.section .text.audio_uart_ft_load_mac_face_526452,"ax"
.global audio_uart_ft_load_mac_face_526452
.thumb_func
audio_uart_ft_load_mac_face_526452: bx lr

.section .text.audio_uart_ft_stream_free_52502a,"ax"
.global audio_uart_ft_stream_free_52502a
.thumb_func
audio_uart_ft_stream_free_52502a: bx lr

.section .text.audio_uart_ft_done_face_526814,"ax"
.global audio_uart_ft_done_face_526814
.thumb_func
audio_uart_ft_done_face_526814: bx lr

.section .text.audio_uart_ft_destroy_face_5258a8,"ax"
.global audio_uart_ft_destroy_face_5258a8
.thumb_func
audio_uart_ft_destroy_face_5258a8: bx lr

.section .text.probe_alloc,"ax"
.global probe_alloc
.thumb_func
probe_alloc: bx lr
