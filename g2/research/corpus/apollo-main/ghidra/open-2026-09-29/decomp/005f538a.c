
undefined4 Ins_ELSE(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 1;
  do {
    iVar1 = SkipCode(param_1);
    if (iVar1 == 1) {
      return param_4;
    }
    if (*(char *)(param_1 + 0x174) == 'X') {
      iVar2 = iVar2 + 1;
    }
    else if (*(char *)(param_1 + 0x174) == 'Y') {
      iVar2 = iVar2 + -1;
    }
  } while (iVar2 != 0);
  return param_4;
}

