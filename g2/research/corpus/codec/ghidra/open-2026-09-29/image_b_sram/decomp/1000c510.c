
void FUN_1000c510(undefined4 param_1,uint param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  
  if ((param_2 & 3) != 0) {
    if (param_3 == 0) {
      return;
    }
    do {
      param_3 = param_3 - 1;
      param_2 = param_2 + 1;
      if (param_3 == 0) {
        return;
      }
    } while ((param_2 & 3) != 0);
  }
  iVar1 = param_2 - 4;
  if (param_3 >> 2 != 0) {
    do {
      iVar1 = iVar1 + 4;
    } while (iVar1 != param_2 + ((param_3 >> 2) + 0x3fffffff) * 4);
  }
  if ((param_3 & 3) == 0) {
    return;
  }
  iVar1 = iVar1 + 3;
  iVar2 = (param_3 & 3) + iVar1;
  do {
    iVar1 = iVar1 + 1;
  } while (iVar1 != iVar2);
  return;
}

