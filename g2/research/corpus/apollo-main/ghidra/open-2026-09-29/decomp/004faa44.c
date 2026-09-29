
undefined8 FUN_004faa44(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  piVar1 = DAT_004fac60;
  local_18 = param_3;
  local_14 = param_4;
  if ((*DAT_004fac60 != 0) && (iVar2 = FUN_0043e2ea(*DAT_004fac60), iVar2 != 0)) {
    FUN_004f92f0();
    FUN_004f5596();
    FUN_004f9484();
    FUN_0043f66c(*piVar1);
    if ((param_2 < 0) || ((int)(uint)*DAT_004fac4c <= param_2)) {
      if (*DAT_004fac4c != 0) {
        *DAT_004fac70 = 0;
      }
    }
    else {
      *DAT_004fac70 = param_2;
    }
    local_18 = 0;
    FUN_004fa2a4(param_1,param_2,4,0);
    piVar1 = DAT_004fac70;
    if ((-1 < *DAT_004fac70) && (*DAT_004fac70 < (int)(uint)*DAT_004fac4c)) {
      FUN_004f70a4(*DAT_004fac70);
      FUN_004f9afc(*piVar1);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_14 = DAT_004fb124;
      local_18 = 0x11a0;
      FUN_0043d574(4,DAT_004fab14,DAT_004fb07c,DAT_004fb128);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004fb12c);
    }
  }
  return CONCAT44(local_14,local_18);
}

