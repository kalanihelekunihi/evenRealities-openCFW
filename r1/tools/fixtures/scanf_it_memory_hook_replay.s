.syntax unified
.thumb
.cpu cortex-m4
.global replay
.thumb_func
replay:
 push {r4-r7,lr}
 sub sp,sp,#12
 cmp r0,#0
 ite pl
 strpl r1,[r2]
 strhmi r1,[r2]
 b done
done:
 movs r0,#0
 add sp,sp,#12
 pop {r4-r7,pc}
