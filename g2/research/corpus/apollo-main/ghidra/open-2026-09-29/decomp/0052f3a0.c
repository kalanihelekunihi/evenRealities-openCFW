
undefined * FUN_0052f3a0(uint param_1)

{
  undefined *puVar1;
  
  if ((param_1 & 3) == 0) {
    if ((int)(param_1 << 0x1e) < 0) {
      if ((int)(param_1 << 0x14) < 0) {
        puVar1 = &DAT_0052f3ec;
      }
      else if ((int)(param_1 << 0x17) < 0) {
        if ((int)(param_1 << 0x15) < 0) {
          puVar1 = &DAT_0052f3f0;
        }
        else {
          puVar1 = &DAT_0052f3ec;
        }
      }
      else {
        puVar1 = &DAT_0052f3f0;
      }
    }
    else {
      puVar1 = &DAT_0052f3f4;
    }
  }
  else if ((int)(param_1 << 0x17) < 0) {
    if ((int)(param_1 << 0x15) < 0) {
      puVar1 = &DAT_0052f3e0;
    }
    else {
      puVar1 = &DAT_0052f3e4;
    }
  }
  else {
    puVar1 = &DAT_0052f3e8;
  }
  return puVar1;
}

