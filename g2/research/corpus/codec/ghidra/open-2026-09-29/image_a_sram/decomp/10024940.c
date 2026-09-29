
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint gx_pmu_get_wakeup_source(void)

{
  uint uVar1;
  
  if ((_DAT_a0000034 & 1) == 0) {
    if ((_DAT_a0000034 & 4) == 0) {
      if ((_DAT_a0000034 & 8) == 0) {
        if ((_DAT_a0000034 & 2) == 0) {
          uVar1 = uRam0000002c & 1;
        }
        else {
          uVar1 = 4;
        }
      }
      else {
        uVar1 = 5;
      }
    }
    else {
      uVar1 = 3;
    }
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

