
undefined * semantic_OtaSelectFlashOps(uint param_1)

{
  undefined *puVar1;
  
  if ((param_1 & 3) == 0) {
    if ((int)(param_1 << 0x1e) < 0) {
      if ((int)(param_1 << 0x14) < 0) {
        puVar1 = &DAT_00444940;
      }
      else if ((int)(param_1 << 0x17) < 0) {
        if ((int)(param_1 << 0x15) < 0) {
          puVar1 = &DAT_00444944;
        }
        else {
          puVar1 = &DAT_00444940;
        }
      }
      else {
        puVar1 = &DAT_00444944;
      }
    }
    else {
      puVar1 = &DAT_00444948;
    }
  }
  else if ((int)(param_1 << 0x17) < 0) {
    if ((int)(param_1 << 0x15) < 0) {
      puVar1 = &DAT_00444934;
    }
    else {
      puVar1 = &DAT_00444938;
    }
  }
  else {
    puVar1 = &DAT_0044493c;
  }
  return puVar1;
}

