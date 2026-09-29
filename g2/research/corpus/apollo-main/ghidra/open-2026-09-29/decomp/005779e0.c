
longlong pt_cmd_77_handler(undefined4 param_1,undefined4 param_2,undefined1 *param_3,
                          undefined1 *param_4)

{
  int iVar1;
  char *pcVar2;
  undefined1 *puVar3;
  
  puVar3 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar3 = (undefined1 *)0xed3;
    FUN_0043d574(3,DAT_00577bbc,DAT_00577bb8,DAT_00577c20,0xed3,DAT_00577c1c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00577c24,DAT_00577c24);
  }
  *param_3 = 0x75;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 1;
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    pcVar2 = (char *)FUN_0044347a();
    if ((pcVar2 != (char *)0x0) && (*pcVar2 == '\x01')) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        puVar3 = (undefined1 *)0xee0;
        FUN_0043d574(3,DAT_00577bbc,DAT_00577bb8,DAT_00577c20,0xee0,DAT_00577c08);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_00577c0c,DAT_00577c0c);
      }
      FUN_004443cc(0x110,0,0);
    }
    param_3[4] = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puVar3 = (undefined1 *)0xee7;
      FUN_0043d574(1,DAT_00577bbc,DAT_00577bb8,DAT_00577c20,0xee7,DAT_00577bf4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00577bf8,DAT_00577bf8);
    }
    param_3[4] = 5;
  }
  *param_4 = 5;
  return ZEXT48(puVar3) << 0x20;
}

