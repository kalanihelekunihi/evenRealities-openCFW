.syntax unified
.thumb
.text
.global entry
.type entry,%function
.thumb_func
entry:
 push {lr}
 bl tail
 movs r0,#0
 pop {pc}
.type tail,%function
.thumb_func
tail:
 lsls r2,r2,#31
 itt cs
 ldrhcs r2,[r1],#2
 strhcs r2,[r0],#2
 itt mi
 ldrbmi r3,[r1]
 strbmi r3,[r0]
 bx lr
