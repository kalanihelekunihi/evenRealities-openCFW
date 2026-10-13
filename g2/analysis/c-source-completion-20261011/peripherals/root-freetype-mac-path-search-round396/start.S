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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-mac-path-search-round396/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096







.section .text.audio_uart_ft_raccess_guess_528470,"ax"
.global audio_uart_ft_raccess_guess_528470
.thumb_func
audio_uart_ft_raccess_guess_528470: bx lr

.section .text.audio_uart_ft_stream_new_524f96,"ax"
.global audio_uart_ft_stream_new_524f96
.thumb_func
audio_uart_ft_stream_new_524f96: bx lr

.section .text.audio_uart_ft_read_mac_resource_5261ac,"ax"
.global audio_uart_ft_read_mac_resource_5261ac
.thumb_func
audio_uart_ft_read_mac_resource_5261ac: bx lr

.section .text.audio_uart_ft_stream_free_52502a,"ax"
.global audio_uart_ft_stream_free_52502a
.thumb_func
audio_uart_ft_stream_free_52502a: bx lr

.section .text.probe_free,"ax"
.global probe_free
.thumb_func
probe_free: bx lr

.section .text.audio_uart_ft_mac_rule_528508,"ax"
.global audio_uart_ft_mac_rule_528508
.thumb_func
audio_uart_ft_mac_rule_528508: bx lr

.section .text.audio_uart_ft_mac_rule_528524,"ax"
.global audio_uart_ft_mac_rule_528524
.thumb_func
audio_uart_ft_mac_rule_528524: bx lr

.section .text.audio_uart_ft_mac_rule_528540,"ax"
.global audio_uart_ft_mac_rule_528540
.thumb_func
audio_uart_ft_mac_rule_528540: bx lr

.section .text.audio_uart_ft_mac_rule_5285d4,"ax"
.global audio_uart_ft_mac_rule_5285d4
.thumb_func
audio_uart_ft_mac_rule_5285d4: bx lr

.section .text.audio_uart_ft_mac_rule_52857e,"ax"
.global audio_uart_ft_mac_rule_52857e
.thumb_func
audio_uart_ft_mac_rule_52857e: bx lr

.section .text.audio_uart_ft_mac_rule_52862c,"ax"
.global audio_uart_ft_mac_rule_52862c
.thumb_func
audio_uart_ft_mac_rule_52862c: bx lr

.section .text.audio_uart_ft_mac_rule_528650,"ax"
.global audio_uart_ft_mac_rule_528650
.thumb_func
audio_uart_ft_mac_rule_528650: bx lr

.section .text.audio_uart_ft_mac_rule_528674,"ax"
.global audio_uart_ft_mac_rule_528674
.thumb_func
audio_uart_ft_mac_rule_528674: bx lr

.section .text.audio_uart_ft_mac_rule_5286b2,"ax"
.global audio_uart_ft_mac_rule_5286b2
.thumb_func
audio_uart_ft_mac_rule_5286b2: bx lr
