
longlong pt_cmd_75_handler(undefined4 param_1,undefined4 param_2,undefined1 *param_3,
                          undefined1 *param_4)

{
  int iVar1;
  undefined1 *puVar2;
  
  puVar2 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (undefined1 *)0xeb5;
    FUN_0043d574(3,DAT_00577bbc,DAT_00577bb8,DAT_00577c14,0xeb5,DAT_00577c10);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00577c18,DAT_00577c18);
  }
  *param_3 = 0x74;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 1;
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    FUN_004441ec(0x110,0,0);
    param_3[4] = 0;
    uled_mspi_setBrightness(100,0x1bbc,0x3f);
    FUN_0046c984(0x60);
    FUN_0046c9dc(0,0);
    FUN_0046c9aa(0x20);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puVar2 = (undefined1 *)0xec9;
      FUN_0043d574(1,DAT_00577bbc,DAT_00577bb8,DAT_00577c14,0xec9,DAT_00577bf4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00577bf8,DAT_00577bf8);
    }
    param_3[4] = 5;
  }
  *param_4 = 5;
  return ZEXT48(puVar2) << 0x20;
}

