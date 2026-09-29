
undefined4 FUN_005c56ca(int param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = FUN_005c5722(param_1);
  if (iVar1 != 0) {
    iVar2 = FUN_0043fe70(param_1);
    iVar3 = FUN_0043fdda(iVar1);
    if (iVar2 < iVar3) {
      iVar2 = FUN_005c45d8(iVar1,0);
      iVar2 = *(int *)(iVar2 + 0xc);
      iVar1 = FUN_005c45e2(iVar1,0);
      FUN_0044ea04(*(undefined4 *)(param_1 + 0x2c),(iVar1 + iVar2) * *(int *)(param_1 + 0x40),
                   param_2);
      FUN_00440656(*(undefined4 *)(param_1 + 0x2c));
    }
  }
  return param_4;
}

