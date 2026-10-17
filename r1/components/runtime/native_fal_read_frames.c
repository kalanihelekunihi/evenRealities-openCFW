/* Native read call frames; reuse existing FAL handle/request state.
 * Symbolic instructions and typed pointer words; no opcode arrays. */
__attribute__((naked,section(".text.r1_native_fal_device_read")))
void r1_native_fal_device_read(void) {
 __asm__ volatile("push {r4,lr}\nmov r4,r2\nmov r2,r0\nldr r0,1f\nmovs r3,#0\nstmia.w r0,{r1,r2,r4}\nmov r2,r0\nldr r0,2f\nmov r1,r3\nldr r0,[r0]\nbl r1_stock_dispatch_10\nmov r0,r4\npop {r4,pc}\n.space 2,0\n1: .word r1_fal_read_request\n2: .word r1_fal_device_handle\n");
}
__attribute__((naked,section(".text.r1_stock_dispatch_10")))
void r1_stock_dispatch_10(void) {
 __asm__ volatile("push {r4,r5}\ncbz r0,2f\nldr r4,[r0,#4]\nldr r4,[r4,#16]\ncbz r4,1f\nmov ip,r4\npop {r4,r5}\nbx ip\n1: movs r0,#2\n3: pop {r4,r5}\nbx lr\n2: movs r0,#1\nb 3b\n");
}
