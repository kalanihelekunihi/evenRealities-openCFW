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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-ps-sfnt-fallback-round381/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096





.section .text.audio_uart_ft_stream_read_ulong_528ba8,"ax"
.global audio_uart_ft_stream_read_ulong_528ba8
.thumb_func
audio_uart_ft_stream_read_ulong_528ba8: bx lr

.section .text.audio_uart_ft_stream_read_ushort_528b4a,"ax"
.global audio_uart_ft_stream_read_ushort_528b4a
.thumb_func
audio_uart_ft_stream_read_ushort_528b4a: bx lr

.section .text.audio_uart_ft_stream_skip_528914,"ax"
.global audio_uart_ft_stream_skip_528914
.thumb_func
audio_uart_ft_stream_skip_528914: bx lr
