
undefined4 pt_cmd_3E_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined1 auStack_40 [40];
  undefined1 *puStack_18;
  
  puStack_18 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_64 = DAT_0057478c;
    local_68 = 0x9ac;
    FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_00574790);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00574794,DAT_00574794);
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_60 = DAT_00574790;
      local_64 = DAT_00574798;
      local_68 = 0x9af;
      FUN_0043d574(1,DAT_00573f80,DAT_00573f7c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057479c,DAT_0057479c,DAT_00574790);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = 0x3e;
    param_3[1] = 1;
    param_3[2] = 2;
    param_3[3] = 1;
    iVar2 = productModeGet();
    if (iVar2 == 1) {
      param_3[4] = 0;
      pcVar1 = DAT_005747a0;
      if (*(char *)(param_1 + 4) == '\x01') {
        if (*DAT_005747a0 == '\x01') {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            local_64 = DAT_005747a4;
            local_68 = 0x9c2;
            FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_00574790);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_005747a8,DAT_005747a8);
          }
          param_3[5] = 4;
          uled_mspi_setBrightness(100,0x1bbc,0x3f);
          *param_4 = 6;
          return 0;
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_64 = DAT_005747ac;
          local_68 = 0x9ca;
          FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_00574790);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_005747b0,DAT_005747b0);
        }
        *pcVar1 = '\x01';
        nvdbSysDtResetAging();
        SVC_SystemTimeSync(*(undefined4 *)(DAT_005747b4 + 4),(int)*(char *)(DAT_005747b4 + 8));
        FUN_004441ec(0x104,0,0);
        service_time_current_calendar_get(auStack_40);
        iVar2 = DAT_00574558;
        FUN_00439c04(DAT_00574558 + 0x30,auStack_40,0x28);
        *(char *)(iVar2 + 0xaa) = *(char *)(iVar2 + 0xaa) + '\x01';
        SVC_NvdbWriteSysData(6,iVar2 + 0x30);
      }
      else if (*(char *)(param_1 + 4) == '\0') {
        if (*DAT_005747a0 == '\0') {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            local_64 = DAT_005747b8;
            local_68 = 0x9df;
            FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_00574790);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_005747bc,DAT_005747bc);
          }
          param_3[5] = 4;
          *param_4 = 6;
          return 0;
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_64 = DAT_005747c0;
          local_68 = 0x9e6;
          FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_00574790);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_005747c4,DAT_005747c4);
        }
        FUN_004443cc(0x104,0,0);
        service_time_current_calendar_get(&local_68);
        iVar2 = DAT_00574558;
        *(undefined1 *)(DAT_00574558 + 0xab) = 1;
        FUN_00439c04(iVar2 + 0x58,&local_68,0x28);
        SVC_NvdbWriteSysData(7,iVar2 + 0x58);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_64 = DAT_00573f68;
        local_68 = 0x9f3;
        FUN_0043d574(1,DAT_00573f80,DAT_00573f7c,DAT_00574790);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0057456c,DAT_0057456c);
      }
      param_3[4] = 5;
    }
    *param_4 = 5;
    uVar3 = 0;
  }
  return uVar3;
}

