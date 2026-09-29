
undefined8
_buzzerPlayStart(undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 *puVar2;
  
  if (param_1 == (undefined1 *)0x0) {
    iVar1 = FUN_0043d0ce();
    puVar2 = param_1;
    if (iVar1 << 0x1e < 0) {
      puVar2 = (undefined1 *)0x10b;
      param_2 = DAT_00502cf8;
      FUN_0043d574(2,DAT_00502cd0,DAT_00502ccc,DAT_00502cfc,0x10b,DAT_00502cf8,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00502d00,DAT_00502d00);
    }
  }
  else {
    puVar2 = param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puVar2 = (undefined1 *)0x10f;
      param_2 = DAT_00502d04;
      FUN_0043d574(4,DAT_00502cd0,DAT_00502ccc,DAT_00502cfc,0x10f,DAT_00502d04,*param_1,param_1[1]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      puVar2 = (undefined1 *)(uint)(byte)param_1[1];
      compress_log_output(0x10800000,DAT_00502d08,DAT_00502d08,*param_1);
    }
    *DAT_00502cb8 = 0;
    *DAT_00502cbc = *param_1;
    *DAT_00502cc0 = (ushort)(byte)param_1[1] * 10;
    *DAT_00502cb4 = param_1 + 2;
    FUN_00480f0c(0x91,*DAT_00502d0c);
    osTimerStart(*DAT_00502cd8,1);
  }
  return CONCAT44(param_2,puVar2);
}

