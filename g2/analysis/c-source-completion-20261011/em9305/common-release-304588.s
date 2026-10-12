.text
.global opencfw_em9305_common_release_304588
.type opencfw_em9305_common_release_304588,@function
opencfw_em9305_common_release_304588:
push_s blink
mpyuw r12,r0,24
mov_s r3,0x801650
add_s r2,r3,r12
ld_s r1,[r2,8]
sub.f r1,r1,1
st_s r1,[r2,8]
bne_s .Lrelease_done
ldb r1,[r3,109]
breq_s r1,0,.Lrelease_done
ldb r1,[r3,108]
brne.nt r1,r0,.Lrelease_done
ld_s r0,[r12,r3]
jl_s.d [r0]
stb 0,[r3,109]
bl opencfw_em9305_pal_release_noop_30fd28
.Lrelease_done:
pop_s blink
j_s [blink]
nop_s
.size opencfw_em9305_common_release_304588,.-opencfw_em9305_common_release_304588
