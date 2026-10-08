.syntax unified
.thumb
.global extended_integrity_boundary
.thumb_func
extended_integrity_boundary:
 bkpt #0
 bx lr
.global extended_history_boundary
.thumb_func
extended_history_boundary:
 bkpt #0
 bx lr
.global extended_merge_boundary
.thumb_func
extended_merge_boundary:
 bkpt #0
 bx lr
.section .note.GNU-stack,"",%progbits
