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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-macbinary-wrapper-round383/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096






.section .text.audio_uart_ft_read_mac_resource_5261ac,"ax"
.global audio_uart_ft_read_mac_resource_5261ac
.thumb_func
audio_uart_ft_read_mac_resource_5261ac: bx lr

.section .text.audio_uart_ft_read_mac_path_526356,"ax"
.global audio_uart_ft_read_mac_path_526356
.thumb_func
audio_uart_ft_read_mac_path_526356: bx lr
