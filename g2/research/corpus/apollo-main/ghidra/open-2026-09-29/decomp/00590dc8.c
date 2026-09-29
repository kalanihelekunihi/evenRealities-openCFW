
int FUN_00590e64(int param_1,int param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  
  if (param_2 == 0x9c4) {
    uVar1 = 0;
LAB_00590e06:
    if (param_1 != 0) {
      if (param_3 == 48000) {
        iVar2 = 5;
      }
      else {
        if (param_3 != DAT_005915a4) {
          return -1;
        }
        iVar2 = 6;
      }
      goto LAB_00590e4c;
    }
  }
  else {
    if (param_2 == 5000) {
      uVar1 = 1;
      goto LAB_00590e06;
    }
    iVar2 = param_1;
    if (param_1 == 0) {
      iVar2 = 0x1d4c;
    }
    if (param_1 != 0 || param_2 != iVar2) {
      if (param_2 == 10000) {
        uVar1 = 3;
      }
      else {
        uVar1 = 4;
      }
      goto LAB_00590e06;
    }
    uVar1 = 2;
  }
  if (param_3 == 8000) {
    iVar2 = 0;
  }
  else if (param_3 == 16000) {
    iVar2 = 1;
  }
  else if (param_3 == 24000) {
    iVar2 = 2;
  }
  else if (param_3 == 32000) {
    iVar2 = 3;
  }
  else {
    if (param_3 != 48000) {
      return -1;
    }
    iVar2 = 4;
  }
LAB_00590e4c:
  if (3 < uVar1) {
    return -1;
  }
  return *(int *)(DAT_005915a8 + iVar2 * 4) * (uVar1 + 1);
}

