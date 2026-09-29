
undefined4 FUN_10004740(int param_1,int param_2,undefined4 param_3,int param_4,undefined4 param_5)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = DAT_100047a0 + param_1 * 0x80;
  if ((param_2 == 0) || (param_4 == 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    *(int *)(iVar2 + 0x6c) = param_4;
    *(undefined4 *)(iVar2 + 0x44) = 2;
    *(int *)(iVar2 + 0x74) = param_2;
    *(undefined4 *)(iVar2 + 0x78) = param_3;
    *(undefined4 *)(iVar2 + 0x70) = param_5;
    *(undefined4 *)(iVar2 + 0x7c) = 0xffffffff;
    if (*(int *)(iVar2 + 0x2c) != 0) {
      *(undefined4 *)(*(int *)(iVar2 + 4) + 0xa8) = 1;
      uVar1 = FUN_100040e8(iVar2);
      return uVar1;
    }
    gx8002_irq_save();
    *(uint *)(*(int *)(iVar2 + 4) + 4) = *(uint *)(*(int *)(iVar2 + 4) + 4) | 2;
    gx8002_irq_restore();
    uVar1 = 0;
  }
  return uVar1;
}

