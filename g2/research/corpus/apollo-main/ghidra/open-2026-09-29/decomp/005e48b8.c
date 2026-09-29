
void FUN_005e48b8(uint param_1)

{
  int iVar1;
  
  iVar1 = DAT_005e53b4;
  if (*(int *)(DAT_005e53b4 + 0x1d8) != 0) {
    if (param_1 < 0x3c) {
      FUN_0049954c(*(undefined4 *)(DAT_005e53b4 + 0x1d8),DAT_005e541c);
    }
    else {
      FUN_0049954c(*(undefined4 *)(DAT_005e53b4 + 0x1d8),DAT_005e5470,param_1 / 0x3c,param_1 % 0x3c)
      ;
    }
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1d8),1);
  }
  return;
}

