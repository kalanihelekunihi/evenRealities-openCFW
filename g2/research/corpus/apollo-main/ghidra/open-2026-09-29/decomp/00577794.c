
longlong pt_cmd_74_handler(undefined4 param_1,undefined4 param_2,undefined1 *param_3,
                          undefined1 *param_4)

{
  int iVar1;
  char *pcVar2;
  undefined1 *puVar3;
  
  puVar3 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar3 = (undefined1 *)0xe97;
    FUN_0043d574(3,DAT_00577bbc,DAT_00577bb8,DAT_00577c00,0xe97,DAT_00577bfc);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00577c04,DAT_00577c04);
  }
  *param_3 = 0x6e;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 1;
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    pcVar2 = (char *)FUN_0044347a();
    if ((pcVar2 != (char *)0x0) && (*pcVar2 == '\x01')) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        puVar3 = (undefined1 *)0xea4;
        FUN_0043d574(3,DAT_00577bbc,DAT_00577bb8,DAT_00577c00,0xea4,DAT_00577c08);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_00577c0c,DAT_00577c0c);
      }
      FUN_004443cc(0x10f,0,0);
    }
    param_3[4] = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puVar3 = (undefined1 *)0xeab;
      FUN_0043d574(1,DAT_00577bbc,DAT_00577bb8,DAT_00577c00,0xeab,DAT_00577bf4);
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

