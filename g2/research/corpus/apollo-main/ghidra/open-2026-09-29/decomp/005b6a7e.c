
void FUN_005b6a7e(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = FUN_005b6a52();
  if (100 < param_2) {
    param_1 = param_1 << 1;
  }
  if (param_1 < 1) {
    if (param_1 < 0) {
      iVar1 = ((param_1 + iVar1) / 0x1c) * 0x1c;
    }
  }
  else {
    iVar1 = ((param_1 + iVar1 + 0x1b) / 0x1c) * 0x1c;
  }
  FUN_005b6a3a(iVar1);
  return;
}

