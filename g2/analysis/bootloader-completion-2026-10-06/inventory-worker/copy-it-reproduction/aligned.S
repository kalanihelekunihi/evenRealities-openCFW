.syntax unified
.thumb
.text
.global entry
.type entry,%function
.thumb_func
entry:
 push {r4,lr}
 bl tail
 movs r0,#0
 pop {r4,pc}
.type tail,%function
.thumb_func
tail:
 subs r2,#16
 blo remainder
 push {r4,r5}
loop:
 ldm r1!,{r3,r4,r5,r12}
 subs r2,#16
 stm r0!,{r3,r4,r5,r12}
 bhs loop
 pop {r4,r5}
remainder:
 lsls r3,r2,#29
 itt cs
 ldmcs r1!,{r3,r12}
 stmcs r0!,{r3,r12}
 itt mi
 ldrmi r3,[r1],#4
 strmi r3,[r0],#4
 lsls r2,r2,#31
 itt cs
 ldrhcs r2,[r1],#2
 strhcs r2,[r0],#2
 itt mi
 ldrbmi r3,[r1]
 strbmi r3,[r0]
 bx lr
