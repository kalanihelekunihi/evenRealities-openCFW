/* Native image-B GSC uses C-SKY frecips at 0x1000c9e0. The CK804EF
 * hard-float ABI passes and returns this scalar in fr0. This named ISA
 * instruction is source, not a copied opcode or a host 1.0f/x substitute.
 * Hardware exception/approximation qualification remains open.
 */
    .text
    .align 2
    .global gx8002_image_b_native_reciprocal_f32
    .type gx8002_image_b_native_reciprocal_f32, @function
gx8002_image_b_native_reciprocal_f32:
    frecips fr0, fr0
    jmp r15
    .size gx8002_image_b_native_reciprocal_f32, .-gx8002_image_b_native_reciprocal_f32
