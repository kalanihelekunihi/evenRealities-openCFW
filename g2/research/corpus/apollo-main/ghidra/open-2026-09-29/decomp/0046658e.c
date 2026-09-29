
void FUN_0046658e(char param_1,byte param_2,undefined1 param_3)

{
  int iVar1;
  
  if (param_2 < 3) {
    if (param_1 == '\0') {
      *(undefined1 *)(DAT_004667ec + (uint)param_2 + 5) = param_3;
    }
    else {
      *(undefined1 *)(DAT_004667ec + (uint)param_2 + 8) = param_3;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00466800,DAT_004667fc,DAT_00466854,0x135,DAT_00466858,param_1,param_2,
                   param_3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_0046685c,DAT_0046685c,param_1,param_2,param_3);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00466800,DAT_004667fc,DAT_00466854,299,DAT_00466848,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00466850,DAT_00466850,param_2);
    }
  }
  return;
}

