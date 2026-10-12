.text
.global opencfw_em9305_command_duration_332be4
.type opencfw_em9305_command_duration_332be4,@function
opencfw_em9305_command_duration_332be4:
breq.nt r1,2,.Lduration_two
brne.nt r1,3,.Lduration_other
brne.d.nt r2,1,.Lduration_coded
add_s r0,r0,5
asl_s r0,r0,4
add r0,r0,382
b_s .Lduration_scale
.Lduration_two:
mov_s r1,44
add2 r0,r1,r0
b_s .Lduration_scale
.Lduration_other:
asl_s r0,r0,3
add1 r0,r0,40
b_s .Lduration_scale
.Lduration_coded:
asl_s r0,r0,6
add3 r0,r0,50
.Lduration_scale:
add r0,r0,873
mpydu 0,r0,0x1a36e3
mov_s r0,226
aslacc r0
mov r0,r58
j_s.d [blink]
mpywhl r0,r0,625
.size opencfw_em9305_command_duration_332be4,.-opencfw_em9305_command_duration_332be4
