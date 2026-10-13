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
.incbin "/tmp/opencfw-main-native.bin"
.macro stub name
.section .text.\name,"ax"
.global \name
.thumb_func
\name: bx lr
.endm
stub audio_uart_font_mem_alloc
stub audio_uart_font_mem_free
stub audio_uart_ft_list_add_529304
stub audio_uart_ft_list_find_5292e6
stub audio_uart_ft_list_remove_529324
stub audio_uart_font_lookup_renderer
stub probe_raster_new
stub probe_raster_done
