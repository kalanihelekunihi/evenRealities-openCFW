
undefined8 FUN_00490b1e(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((*(byte *)(param_2 + 0x16) & 0x30) == 0x30) {
    if (**(short **)(param_2 + 0x20) != *(short *)(param_2 + 0x10)) {
      uVar1 = 1;
      goto LAB_00490bc6;
    }
  }
  else if ((*(byte *)(param_2 + 0x16) & 0x30) == 0x10) {
    if (*(int *)(param_2 + 0x20) == 0) {
      if (((*(byte *)(param_2 + 0x16) & 0xc0) == 0) && (iVar2 = FUN_0049087a(param_2), iVar2 != 0))
      {
        uVar1 = 1;
        goto LAB_00490bc6;
      }
    }
    else {
      iVar2 = FUN_00490678(*(undefined4 *)(param_2 + 0x20));
      if (iVar2 == 0) {
        uVar1 = 1;
        goto LAB_00490bc6;
      }
    }
  }
  if (*(int *)(param_2 + 0x1c) == 0) {
    if ((*(byte *)(param_2 + 0x16) & 0x30) == 0) {
      uVar1 = DAT_004910c8;
      if (*(int *)(param_1 + 0x10) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0x10);
      }
      *(undefined4 *)(param_1 + 0x10) = uVar1;
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  else if ((*(byte *)(param_2 + 0x16) & 0xc0) == 0x40) {
    uVar1 = FUN_00490aea(param_1,param_2);
  }
  else if ((*(byte *)(param_2 + 0x16) & 0x30) == 0x20) {
    uVar1 = FUN_00490690(param_1,param_2);
  }
  else {
    uVar1 = FUN_00490a46(param_1,param_2);
  }
LAB_00490bc6:
  return CONCAT44(param_4,uVar1);
}

