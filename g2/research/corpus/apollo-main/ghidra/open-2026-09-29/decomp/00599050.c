
int FUN_00599050(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (4 < param_1) {
    return 0;
  }
  iVar1 = (int)~-(uint)(param_1 == 0) >> 0x1f;
  if (param_1 < 2) {
    iVar2 = 0;
  }
  else {
    iVar2 = 1;
    if (3 < param_1) {
      return 2 - iVar1;
    }
  }
  return iVar2 - iVar1;
}

