.text
.global report
report:
st.aw blink,[sp,-24]
mov_s r12,sp
sth_s r1,[r12,10]
stb_s r0,[sp,8]
mov_s r1,34
sth_s r0,[r12,4]
add_s r0,sp,4
st r4,[sp,20]
st_s r3,[sp,16]
sth_s r2,[r12,12]
bl.d target
sth_s r1,[r12,6]
ld.ab blink,[sp,24]
j_s [blink]
