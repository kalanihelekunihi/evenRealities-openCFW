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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-ps-sfnt-fallback-round381/connected-oracle.bin"
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

.section .text.audio_uart_ft_stream_seek_5288e0,"ax"
.global audio_uart_ft_stream_seek_5288e0
.thumb_func
audio_uart_ft_stream_seek_5288e0: bx lr

.section .text.audio_uart_ft_stream_read_528928,"ax"
.global audio_uart_ft_stream_read_528928
.thumb_func
audio_uart_ft_stream_read_528928: bx lr

.section .text.audio_uart_ft_get_module_5273b8,"ax"
.global audio_uart_ft_get_module_5273b8
.thumb_func
audio_uart_ft_get_module_5273b8: bx lr

.section .text.audio_uart_ft_open_face_internal_5264a6,"ax"
.global audio_uart_ft_open_face_internal_5264a6
.thumb_func
audio_uart_ft_open_face_internal_5264a6: bx lr

.section .text.probe_alloc,"ax"
.global probe_alloc
.thumb_func
probe_alloc: bx lr

.section .text.probe_free,"ax"
.global probe_free
.thumb_func
probe_free: bx lr
