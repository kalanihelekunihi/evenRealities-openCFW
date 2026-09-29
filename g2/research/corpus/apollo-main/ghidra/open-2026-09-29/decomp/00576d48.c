
longlong pt_cmd_65_handler(undefined4 param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined1 *puVar2;
  
  puVar2 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0xdb6;
    FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_0057778c,0xdb6,DAT_00577788,puVar2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00577790,DAT_00577790);
  }
  *param_3 = 100;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 1;
  param_3[4] = *(undefined1 *)(DAT_0057756c + 0x2e);
  *param_4 = 5;
  return (ulonglong)param_2 << 0x20;
}

