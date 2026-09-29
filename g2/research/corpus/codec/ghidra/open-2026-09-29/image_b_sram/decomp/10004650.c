
undefined4 FUN_10004650(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = param_1 * 0x80 + DAT_10004680;
  if (param_2 != 0) {
    *(undefined4 *)(iVar1 + 0x44) = 1;
    *(int *)(iVar1 + 0x48) = param_2;
    *(undefined4 *)(iVar1 + 0x4c) = param_3;
    gx8002_irq_save();
    *(uint *)(*(int *)(iVar1 + 4) + 4) = *(uint *)(*(int *)(iVar1 + 4) + 4) | 2;
    gx8002_irq_restore();
    return 0;
  }
  return 0xffffffff;
}

