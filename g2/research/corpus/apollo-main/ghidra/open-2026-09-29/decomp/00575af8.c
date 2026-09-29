
undefined4 pt_cmd_58_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 local_38;
  undefined1 local_37;
  undefined1 local_36;
  undefined1 local_35;
  undefined1 local_34;
  undefined1 local_33;
  undefined1 local_32;
  undefined1 local_31;
  undefined4 local_30;
  undefined4 local_2c;
  undefined1 *puStack_18;
  
  puStack_18 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00575e98,DAT_00575e94,DAT_00576504,0xc79,DAT_00576500);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00576508,DAT_00576508);
  }
  if ((((param_1 == 0) || (param_3 == (undefined1 *)0x0)) || (param_4 == (undefined1 *)0x0)) ||
     (param_2 < 8)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00575e98,DAT_00575e94,DAT_00576504,0xc7b,DAT_0057650c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00576510,DAT_00576510);
    }
    return 0xffffffff;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_00575e98,DAT_00575e94,DAT_00576504,0xc7e,DAT_00576514,
                 *(undefined1 *)(param_1 + 4),*(undefined1 *)(param_1 + 5),
                 *(undefined1 *)(param_1 + 6),*(undefined1 *)(param_1 + 7));
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x9000000,DAT_005766fc,DAT_005766fc,*(undefined1 *)(param_1 + 4),
                        *(undefined1 *)(param_1 + 5),*(undefined1 *)(param_1 + 6),
                        *(undefined1 *)(param_1 + 7));
  }
  iVar1 = file_open(DAT_00576700,&DAT_00575e78);
  if (iVar1 != 0) {
    file_read(&local_38,1,0x20,iVar1);
    file_close(iVar1);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00575e98,DAT_00575e94,DAT_00576504,0xc8d,DAT_0057670c,local_38,local_37,
                   local_36,local_35);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x9000000,DAT_00576710,DAT_00576710,local_38,local_37,local_36,local_35);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00575e98,DAT_00575e94,DAT_00576504,0xc8e,DAT_005767f0,local_34,local_33,
                   local_32,local_31);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x9000000,DAT_005767f4,DAT_005767f4,local_34,local_33,local_32,local_31);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00575e98,DAT_00575e94,DAT_00576504,0xc8f,DAT_005767f8,local_30);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_005767fc,DAT_005767fc,local_30);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00575e98,DAT_00575e94,DAT_00576504,0xc90,DAT_005768a8,local_2c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_005768ac,DAT_005768ac,local_2c);
    }
    *DAT_00576a28 = local_2c;
    *param_3 = 0x58;
    param_3[1] = 1;
    param_3[2] = 2;
    param_3[3] = 0x20;
    FUN_00439be4(param_3 + 4,&local_38,0x20);
    *param_4 = 0x24;
    return 0;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(1,DAT_00575e98,DAT_00575e94,DAT_00576504,0xc84,DAT_00576704);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_00576708,DAT_00576708);
  }
  uVar2 = pt_handler_result(0x58,1,2,param_3,param_4);
  return uVar2;
}

