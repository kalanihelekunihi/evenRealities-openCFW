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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-destroy-face-round372/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096





.section .text.audio_uart_ft_done_glyph_slot_5253f4,"ax"
.global audio_uart_ft_done_glyph_slot_5253f4
.thumb_func
audio_uart_ft_done_glyph_slot_5253f4: bx lr

.section .text.audio_uart_ft_list_finalize_529378,"ax"
.global audio_uart_ft_list_finalize_529378
.thumb_func
audio_uart_ft_list_finalize_529378: bx lr

.section .text.audio_uart_ft_destroy_charmaps_52586e,"ax"
.global audio_uart_ft_destroy_charmaps_52586e
.thumb_func
audio_uart_ft_destroy_charmaps_52586e: bx lr

.section .text.audio_uart_ft_stream_free_52502a,"ax"
.global audio_uart_ft_stream_free_52502a
.thumb_func
audio_uart_ft_stream_free_52502a: bx lr

.section .text.audio_uart_ft_destroy_size_525832,"ax"
.global audio_uart_ft_destroy_size_525832
.thumb_func
audio_uart_ft_destroy_size_525832: bx lr

.section .text.probe_autohint,"ax"
.global probe_autohint
.thumb_func
probe_autohint: bx lr

.section .text.probe_generic,"ax"
.global probe_generic
.thumb_func
probe_generic: bx lr

.section .text.probe_class,"ax"
.global probe_class
.thumb_func
probe_class: bx lr

.section .text.probe_free,"ax"
.global probe_free
.thumb_func
probe_free: bx lr
