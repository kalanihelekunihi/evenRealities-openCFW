
undefined8 FUN_0048b86c(undefined4 param_1,int param_2,byte param_3,uint param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = param_4;
  if (param_4 == 0) {
    uVar1 = FUN_0048aad8(param_1,param_3);
  }
  iVar2 = param_2 * uVar1;
  if (param_3 == 0x14) {
    iVar2 = param_2 * (uVar1 >> 1) + iVar2;
  }
  else if (param_3 - 7 < 4) {
    if (param_3 == 7) {
      iVar3 = 2;
    }
    else if (param_3 == 8) {
      iVar3 = 4;
    }
    else if (param_3 == 9) {
      iVar3 = 0x10;
    }
    else if (param_3 == 10) {
      iVar3 = 0x100;
    }
    else {
      iVar3 = 0;
    }
    iVar2 = iVar2 + iVar3 * 4;
  }
  return CONCAT44(param_4,iVar2);
}

