
undefined8 sched_hiprio_call(void)

{
  int iVar1;
  int unaff_r6;
  undefined4 in_stack_00000000;
  
  iVar1 = mspi_cq_pause();
  if (iVar1 == 0) {
    *(undefined4 *)(unaff_r6 + 0x24) = 0;
    iVar1 = DAT_00424bd8;
    *(undefined4 *)(DAT_00424bd8 + *(int *)(unaff_r6 + 4) * 0x1000 + 0x208) = 0x40;
    *(uint *)(iVar1 + *(int *)(unaff_r6 + 4) * 0x1000 + 0x200) =
         *(uint *)(iVar1 + *(int *)(unaff_r6 + 4) * 0x1000 + 0x200) | 0x40;
    *(undefined1 *)(unaff_r6 + 0x83c) = 1;
    iVar1 = program_dma();
  }
  return CONCAT44(in_stack_00000000,iVar1);
}

