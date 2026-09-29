
undefined * FUN_004d58d8(uint param_1)

{
  undefined *puVar1;
  
  if ((param_1 & 3) == 0) {
    if ((int)(param_1 << 0x1e) < 0) {
      if ((int)(param_1 << 0x14) < 0) {
        puVar1 = &DAT_004d5924;
      }
      else if ((int)(param_1 << 0x17) < 0) {
        if ((int)(param_1 << 0x15) < 0) {
          puVar1 = &DAT_004d5928;
        }
        else {
          puVar1 = &DAT_004d5924;
        }
      }
      else {
        puVar1 = &DAT_004d5928;
      }
    }
    else {
      puVar1 = &DAT_004d592c;
    }
  }
  else if ((int)(param_1 << 0x17) < 0) {
    if ((int)(param_1 << 0x15) < 0) {
      puVar1 = &DAT_004d5918;
    }
    else {
      puVar1 = &DAT_004d591c;
    }
  }
  else {
    puVar1 = &DAT_004d5920;
  }
  return puVar1;
}

