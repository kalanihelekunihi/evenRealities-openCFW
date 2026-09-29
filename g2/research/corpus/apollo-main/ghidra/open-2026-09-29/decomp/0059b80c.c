
undefined4 FUN_0059b80c(int param_1,int param_2,undefined1 *param_3)

{
  int iVar1;
  int iVar2;
  undefined1 uVar3;
  bool bVar4;
  
  iVar1 = FUN_0059b6a0();
  iVar2 = param_1;
  if (iVar1 != 0) {
    iVar2 = param_1 + -1;
  }
  if (param_3 != (undefined1 *)0x0) {
    if ((param_2 < (iVar2 + 3) * 0x14) || (5 < param_1)) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
    *param_3 = uVar3;
  }
  iVar1 = (iVar2 + 1) * 0x14;
  bVar4 = SBORROW4(iVar1,param_2);
  iVar2 = iVar1 - param_2;
  if (iVar1 < param_2) {
    bVar4 = SBORROW4(param_1,6);
    iVar2 = param_1 + -6;
  }
  if (iVar2 < 0 != bVar4) {
    return 1;
  }
  return 0;
}

