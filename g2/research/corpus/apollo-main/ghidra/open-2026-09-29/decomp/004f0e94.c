
undefined8 FUN_004f0e94(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  if (((-1 < param_1) && (param_1 < *DAT_004f188c)) && (*(int *)(DAT_004f1890 + param_1 * 4) != 0))
  {
    FUN_0044130c(*(undefined4 *)(DAT_004f1890 + param_1 * 4),0,0);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar2 = 0x281;
      param_2 = DAT_004f18a4;
      FUN_0043d574(4,DAT_004f18a0,DAT_004f189c,DAT_004f18a8,0x281,DAT_004f18a4,param_1,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004f19e4,DAT_004f19e4,param_1);
    }
  }
  return CONCAT44(param_2,iVar2);
}

