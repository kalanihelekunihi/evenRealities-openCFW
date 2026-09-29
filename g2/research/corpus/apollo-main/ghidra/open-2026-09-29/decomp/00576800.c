
undefined4 pt_cmd_61_handler(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_005771c8,0xd56,DAT_005771c4,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_00576844;
  }
  compress_log_output(0xc000000,DAT_005771cc,DAT_005771cc);
LAB_00576844:
  uVar1 = *(undefined1 *)(param_1 + 4);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_005771c8,0xd58,DAT_005771d0,uVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_00577348,DAT_00577348,uVar1);
  }
  iVar2 = DAT_0057756c;
  *(undefined1 *)(DAT_0057756c + 0x2e) = uVar1;
  SVC_NvdbWriteSysData(5,iVar2 + 0x2e);
  return 0;
}

