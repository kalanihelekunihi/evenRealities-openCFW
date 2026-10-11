.syntax unified
.thumb
.section .text.g2_flashdb_vformat,"ax",%progbits
.global g2_flashdb_vformat
.type g2_flashdb_vformat,%function
.thumb_func
g2_flashdb_vformat:
    b.w audio_heap_formatter
.size g2_flashdb_vformat, .-g2_flashdb_vformat
