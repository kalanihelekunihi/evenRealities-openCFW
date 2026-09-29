
undefined8 FUN_004b0b5a(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = param_3;
  if (param_1 == 0) {
    param_1 = FUN_004c791a();
  }
  iVar1 = *(int *)(param_1 + 0x40);
  if (((iVar1 == 0) || ((*(uint *)(iVar1 + 4) & 0xffff) != param_2)) ||
     (*(uint *)(iVar1 + 4) >> 0x10 != param_3)) {
    if (iVar1 == 0) {
      uVar2 = FUN_0048affa(param_2,param_3,0xe,0);
      *(undefined4 *)(param_1 + 0x40) = uVar2;
    }
    else {
      uVar3 = 0;
      iVar1 = FUN_0048b196(iVar1,0xe,param_2,param_3,0,param_4);
      if (iVar1 == 0) {
        FUN_0048b216(*(undefined4 *)(param_1 + 0x40));
        uVar2 = FUN_0048affa(param_2,param_3,0xe,0);
        *(undefined4 *)(param_1 + 0x40) = uVar2;
      }
      else {
        *(int *)(param_1 + 0x40) = iVar1;
      }
    }
    if (*(int *)(param_1 + 0x40) == 0) {
      uVar3 = DAT_004b1084;
      FUN_0044d25c(3,DAT_004b1054,0x1e2,DAT_004b1088);
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(uVar3,uVar2);
}

