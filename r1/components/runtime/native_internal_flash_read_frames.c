/* Native registered flash read policy and mapped byte-copy frames.
 * Existing flash record/context remain the sole state owners. */
__attribute__((naked,section(".text.r1_internal_flash_device_read")))
void r1_internal_flash_device_read(void) {
 __asm__ volatile("push {r4,r5,r6,lr}\nmovs r4,r2\nbeq 1f\nldr r5,4f\nldrb r0,[r5,#4]\ncbz r0,2f\nldrb r0,[r5,#8]\ncbz r0,3f\nldr r0,[r5,#12]\nblx r0\nldrh r0,[r4,#8]\nuxth r1,r0\nldmia r4!,{r0,r2}\nbl r1_internal_flash_mapped_read\nldr r0,[r5,#16]\nblx r0\nb 5f\n1: movs r0,#26\npop {r4,r5,r6,pc}\n2: movs r0,#27\npop {r4,r5,r6,pc}\n3: ldrh r0,[r4,#8]\nuxth r1,r0\nldmia r4!,{r0,r2}\nbl r1_internal_flash_mapped_read\n5: movs r0,#0\npop {r4,r5,r6,pc}\n.space 2,0\n4: .word r1_internal_flash_record\n");
}
__attribute__((naked,section(".text.r1_internal_flash_mapped_read")))
void r1_internal_flash_mapped_read(void) {
 __asm__ volatile("push {r4,lr}\nldr r4,1f\nmovs r3,#0\nldr r4,[r4,#12]\nadd r2,r4\nb 3f\n2: ldrb r4,[r2,r3]\nstrb r4,[r0,r3]\nadds r3,r3,#1\n3: cmp r3,r1\nbcc 2b\npop {r4,pc}\n1: .word r1_internal_flash_context\n");
}
