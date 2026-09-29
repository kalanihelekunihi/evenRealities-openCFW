
int service_even_ai_fn_00497e08(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    iVar2 = 0x4b;
    param_2 = DAT_004985b0;
    param_3 = param_1;
    FUN_0043d574(4,DAT_004985bc,DAT_004985b8,DAT_004985b4,0x4b,DAT_004985b0,param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00497e52;
  }
  compress_log_output(0x10400000,DAT_004985c0,DAT_004985c0,param_1,iVar2,param_2,param_3);
LAB_00497e52:
  if (param_1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004985bc,DAT_004985b8,DAT_004985b4,0x4d,DAT_004985c4,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004985c8,DAT_004985c8,param_1);
    }
  }
  return param_1;
}

