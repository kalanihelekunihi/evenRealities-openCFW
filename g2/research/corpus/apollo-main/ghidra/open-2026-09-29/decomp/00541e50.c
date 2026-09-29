
undefined4 smpDbRecordInUse(int param_1)

{
  undefined4 uVar1;
  
  if (*(char *)(param_1 + 7) == '\0') {
    if (*(int *)(param_1 + 0xc) == 0) {
      if (*(short *)(param_1 + 8) == 0) {
        uVar1 = 0;
      }
      else {
        uVar1 = 1;
      }
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

