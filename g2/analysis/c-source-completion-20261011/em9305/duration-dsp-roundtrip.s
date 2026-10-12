.text
.global opencfw_duration_dsp_roundtrip
opencfw_duration_dsp_roundtrip:
mpydu 0,r0,0x1a36e3
aslacc 0xe2
mov r0,r58
j_s.d [blink]
mpywhl r0,r0,625
