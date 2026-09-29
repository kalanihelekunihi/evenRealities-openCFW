
longlong pt_cmd_F3_handler(undefined4 param_1,undefined4 param_2,undefined1 *param_3,
                          undefined1 *param_4)

{
  int iVar1;
  undefined1 *puVar2;
  
  puVar2 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (undefined1 *)0xef1;
    FUN_0043d574(3,DAT_00577bbc,DAT_00577bb8,DAT_00577c2c,0xef1,DAT_00577c28);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00577c30,DAT_00577c30);
  }
  *param_3 = 0x77;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 1;
  param_3[4] = 0;
  input_msg_send_id3();
  *param_4 = 5;
  return ZEXT48(puVar2) << 0x20;
}

