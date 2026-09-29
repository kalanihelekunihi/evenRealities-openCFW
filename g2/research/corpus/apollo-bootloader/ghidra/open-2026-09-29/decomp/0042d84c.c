
undefined * stream_mode_42d84c(uint param_1)

{
  undefined *puVar1;
  
  if ((param_1 & 3) == 0) {
    if ((int)(param_1 << 0x1e) < 0) {
      if ((int)(param_1 << 0x14) < 0) {
        puVar1 = &DAT_0042dadc;
      }
      else if ((int)(param_1 << 0x17) < 0) {
        if ((int)(param_1 << 0x15) < 0) {
          puVar1 = &DAT_0042dae0;
        }
        else {
          puVar1 = &DAT_0042dadc;
        }
      }
      else {
        puVar1 = &DAT_0042dae0;
      }
    }
    else {
      puVar1 = &DAT_0042dae4;
    }
  }
  else if ((int)(param_1 << 0x17) < 0) {
    if ((int)(param_1 << 0x15) < 0) {
      puVar1 = &DAT_0042dad0;
    }
    else {
      puVar1 = &DAT_0042dad4;
    }
  }
  else {
    puVar1 = &DAT_0042dad8;
  }
  return puVar1;
}

