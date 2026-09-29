
undefined4 FUN_10004684(int param_1)

{
  int iVar1;
  
  iVar1 = param_1 * 0x80 + DAT_100046a8;
  *(undefined4 *)(iVar1 + 0x48) = 0;
  *(undefined4 *)(iVar1 + 0x4c) = 0;
  gx8002_irq_save();
  *(uint *)(*(int *)(iVar1 + 4) + 4) = *(uint *)(*(int *)(iVar1 + 4) + 4) & 0xfffffffd;
  gx8002_irq_restore();
  return 0;
}

