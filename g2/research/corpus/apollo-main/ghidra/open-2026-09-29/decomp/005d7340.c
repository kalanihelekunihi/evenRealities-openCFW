
uint FUN_005d7340(int param_1,uint param_2,char param_3)

{
  uint uVar1;
  int iVar2;
  
  if ((int)param_2 < 0x41) {
    uVar1 = 0x40;
  }
  else {
    iVar2 = param_2 - *(int *)(param_1 + 8);
    if (iVar2 < 0) {
      iVar2 = -iVar2;
    }
    if ((iVar2 < 0x28) && (param_2 = *(uint *)(param_1 + 8), (int)param_2 < 0x30)) {
      param_2 = 0x30;
    }
    if ((int)param_2 < 0xc0) {
      uVar1 = param_2 & 0x3f;
      param_2 = param_2 & 0xffffffc0;
      if (uVar1 < 10) {
        uVar1 = uVar1 + param_2;
      }
      else if (uVar1 < 0x20) {
        uVar1 = param_2 + 10;
      }
      else if (uVar1 < 0x36) {
        uVar1 = param_2 + 0x36;
      }
      else {
        uVar1 = uVar1 + param_2;
      }
    }
    else {
      uVar1 = param_2 + 0x20 & 0xffffffc0;
    }
  }
  if (param_3 != '\0') {
    uVar1 = uVar1 + 0x20 & 0xffffffc0;
  }
  return uVar1;
}

