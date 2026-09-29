
undefined4 pt_cmd_5B_handler(int param_1,byte param_2,int param_3,int param_4)

{
  char cVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_00576fc0,0xd13,DAT_00576fbc);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00576fc4,DAT_00576fc4);
  }
  piVar2 = DAT_00576a3c;
  if ((((param_1 != 0) && (param_3 != 0)) && (param_4 != 0)) && (8 < param_2)) {
    if (*DAT_00576a3c != 0) {
      file_close(*DAT_00576a3c);
      *piVar2 = 0;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_00576fc0,0xd1d,DAT_005770b8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_005770bc,DAT_005770bc);
      }
    }
    *DAT_00576a48 = 0;
    *DAT_00576a4c = 0;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_00576fc0,0xd23,DAT_005770c0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_005770c4,DAT_005770c4);
    }
    cVar1 = *(char *)(param_1 + 4);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005768bc,DAT_005768b8,DAT_00576fc0,0xd28,DAT_005770c8,cVar1,
                   *(undefined1 *)(param_1 + 5),*(undefined1 *)(param_1 + 6),
                   *(undefined1 *)(param_1 + 7),*(undefined1 *)(param_1 + 8));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x9400000,DAT_00577344,DAT_00577344,cVar1,*(undefined1 *)(param_1 + 5),
                          *(undefined1 *)(param_1 + 6),*(undefined1 *)(param_1 + 7),
                          *(undefined1 *)(param_1 + 8));
    }
    if (cVar1 == '\0') {
      uVar4 = pt_handler_result(0x5b,0,2,param_3,param_4);
    }
    else {
      uVar4 = pt_handler_result(0x5b,1,2,param_3,param_4);
    }
    return uVar4;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_00576fc0,0xd15,DAT_00576fc8);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_00576fcc,DAT_00576fcc);
  }
  return 0xffffffff;
}

