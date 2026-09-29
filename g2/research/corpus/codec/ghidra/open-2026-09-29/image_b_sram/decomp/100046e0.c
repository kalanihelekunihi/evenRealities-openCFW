
undefined4 FUN_100046e0(int param_1)

{
  int iVar1;
  
  iVar1 = param_1 * 0x80 + DAT_10004704;
  *(undefined4 *)(iVar1 + 0x50) = 0;
  *(undefined4 *)(iVar1 + 0x54) = 0;
  gx8002_irq_save();
  *(uint *)(*(int *)(iVar1 + 4) + 4) = *(uint *)(*(int *)(iVar1 + 4) + 4) & 0xfffffffe;
  gx8002_irq_restore();
  return 0;
}

