
undefined4 FUN_005ece4c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = DAT_005ed9c4;
  FUN_005eceb2();
  FUN_005ed1d6();
  FUN_005ea30c();
  if ((((*(int *)(iVar1 + 0x1cc) != 0) && (*(int *)(iVar1 + 0x1d0) != 0)) &&
      (*(int *)(iVar1 + 0x1d4) != 0)) && (*(int *)(iVar1 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1cc),1);
    FUN_005e47fe(*(undefined4 *)(iVar1 + 0x1d0),DAT_005ed9bc);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),param_1);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1dc),&LAB_005ed0b4);
  }
  *(undefined1 *)(iVar1 + 0x27d) = 1;
  return param_4;
}

