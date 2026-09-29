
void DRV_BuzzerPlayNote(undefined1 param_1,undefined1 param_2,undefined1 param_3)

{
  undefined1 *puVar1;
  int iVar2;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00502cd0,DAT_00502ccc,DAT_00502d40,0x14c,DAT_00502d3c,param_1,param_2,param_3
                );
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xcc00000,DAT_00502d44,DAT_00502d44,param_1,param_2,param_3);
  }
  puVar1 = DAT_00502d48;
  *DAT_00502d48 = 1;
  puVar1[1] = 0;
  puVar1[2] = param_1;
  puVar1[3] = param_2;
  puVar1[4] = param_3;
  puVar1[5] = 0;
  puVar1[6] = 0;
  puVar1[7] = 0;
  _buzzerPlayStop();
  _buzzerPlayStart(puVar1);
  return;
}

