
undefined8 FUN_004fb290(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  uint *puVar2;
  int iVar3;
  
  puVar2 = DAT_004fb734;
  piVar1 = DAT_004fb71c;
  if (*DAT_004fb71c == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0xba;
      param_3 = DAT_004fb720;
      FUN_0043d574(2,DAT_004fb70c,DAT_004fb708,DAT_004fb724,0xba,DAT_004fb720,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004fb728,DAT_004fb728);
    }
  }
  else if (param_1 < 2) {
    if ((param_1 != *DAT_004fb734) && (*DAT_004fb738 == 0)) {
      *DAT_004fb734 = param_1;
      FUN_004fb1fa(*puVar2);
      FUN_0050029c(*puVar2 + 1);
      FUN_004fb568(*piVar1,param_1 << 8,0xfa);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0xbf;
      param_3 = DAT_004fb72c;
      FUN_0043d574(2,DAT_004fb70c,DAT_004fb708,DAT_004fb724,0xbf,DAT_004fb72c,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004fb730,DAT_004fb730,param_1);
    }
  }
  return CONCAT44(param_3,param_2);
}

