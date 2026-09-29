
undefined8 FUN_005d9abc(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = param_1 * 0x18 + DAT_005d9b58;
  iVar3 = iVar1 + 0x18;
  uVar2 = *(uint *)(iVar1 + 0x2c);
  if (uVar2 == 0) {
    uVar2 = FUN_005d9aa2(iVar3);
    if (uVar2 < param_3) {
      param_3 = 0;
    }
    else {
      FUN_005d9a44(iVar3,param_2,param_3);
    }
  }
  else if (uVar2 == 2) {
    param_3 = FUN_005d99c0(iVar3,param_2,param_3);
  }
  else if (uVar2 < 2) {
    uVar2 = FUN_005d9aa2(iVar3);
    if (param_3 <= uVar2) {
      uVar2 = param_3;
    }
    param_3 = uVar2;
    FUN_005d9a44(iVar3,param_2,param_3);
  }
  else {
    param_3 = 0;
  }
  return CONCAT44(param_4,param_3);
}

