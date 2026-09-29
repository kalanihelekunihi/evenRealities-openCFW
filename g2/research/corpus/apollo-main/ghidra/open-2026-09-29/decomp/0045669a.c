
undefined * FUN_0045669a(uint param_1)

{
  undefined *puVar1;
  
  if ((param_1 & 3) == 0) {
    if ((int)(param_1 << 0x1e) < 0) {
      if ((int)(param_1 << 0x14) < 0) {
        puVar1 = &DAT_004567ac;
      }
      else if ((int)(param_1 << 0x17) < 0) {
        if ((int)(param_1 << 0x15) < 0) {
          puVar1 = &DAT_004567b0;
        }
        else {
          puVar1 = &DAT_004567ac;
        }
      }
      else {
        puVar1 = &DAT_004567b0;
      }
    }
    else {
      puVar1 = &DAT_004567b4;
    }
  }
  else if ((int)(param_1 << 0x17) < 0) {
    if ((int)(param_1 << 0x15) < 0) {
      puVar1 = &DAT_004567a0;
    }
    else {
      puVar1 = &DAT_004567a4;
    }
  }
  else {
    puVar1 = &DAT_004567a8;
  }
  return puVar1;
}

