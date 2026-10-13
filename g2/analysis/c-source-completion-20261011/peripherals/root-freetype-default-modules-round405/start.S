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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-default-modules-round405/oracle-data-bound.bin"
.section .text.audio_uart_ft_add_module_52729c,"ax"
.global audio_uart_ft_add_module_52729c
.thumb_func
audio_uart_ft_add_module_52729c: bx lr
.macro clazz name
.section .rodata.\name,"a"
.balign 4
.global \name
\name: .word 0
.endm
clazz autofit_module_class
clazz tt_driver_class
clazz cff_driver_class
clazz psaux_module_class
clazz psnames_module_class
clazz pshinter_module_class
clazz sfnt_module_class
clazz ft_smooth_renderer_class
clazz ft_smooth_lcd_renderer_class
clazz ft_smooth_lcdv_renderer_class
