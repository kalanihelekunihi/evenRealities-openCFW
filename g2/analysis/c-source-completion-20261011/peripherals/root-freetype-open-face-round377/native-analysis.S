.syntax unified
.thumb
.section .native,"ax"
.global native_payload_start
native_payload_start:
.incbin "/tmp/opencfw-main-native.bin"
.global ft_open_face_native
.type ft_open_face_native,%function
.set ft_open_face_native,native_payload_start+0xee4a7
.size ft_open_face_native,840
