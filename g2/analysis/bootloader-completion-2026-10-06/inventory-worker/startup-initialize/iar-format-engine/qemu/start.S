.syntax unified
.thumb
.section .vectors,"a"
.word 0x20080000
.word reset_entry
.rept 14
.word fault_entry
.endr
.text
.global reset_entry
.thumb_func
reset_entry:
 bl main
 b .
.global fault_entry
.thumb_func
fault_entry:
 b .
