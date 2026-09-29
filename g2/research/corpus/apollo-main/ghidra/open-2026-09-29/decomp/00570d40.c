
undefined4 pt_cmd_18_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  char cVar1;
  int *piVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  int local_28;
  undefined4 local_24;
  undefined1 *local_20;
  undefined1 *puStack_1c;
  
  piVar2 = DAT_00571388;
  local_28 = param_1;
  local_24 = param_2;
  local_20 = param_3;
  puStack_1c = param_4;
  if (*DAT_00571388 != 0) {
    file_heap_free(*DAT_00571388);
    *piVar2 = 0;
  }
  *DAT_0057138c = 0;
  *DAT_00571390 = 0;
  *DAT_00571394 = 0;
  FUN_0043c0e4(DAT_00571398,0x20,0);
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    local_20 = (undefined1 *)(uint)*(byte *)(param_1 + 4);
    local_24 = DAT_0057139c;
    local_28 = 0x54f;
    FUN_0043d574(3,DAT_00571054,DAT_00571050,DAT_005713a0);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_005713a4,DAT_005713a4,*(undefined1 *)(param_1 + 4));
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 6)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_20 = DAT_005713a0;
      local_24 = DAT_0057105c;
      local_28 = 0x552;
      FUN_0043d574(1,DAT_00571054,DAT_00571050);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00571060,DAT_00571060,DAT_005713a0);
    }
    uVar5 = 0xffffffff;
  }
  else {
    cVar1 = *(char *)(param_1 + 4);
    *param_3 = 0x19;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 2;
    iVar4 = productModeGet();
    if (iVar4 == 1) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_24 = DAT_005713a8;
        local_28 = 0x561;
        FUN_0043d574(3,DAT_00571054,DAT_00571050,DAT_005713a0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_005713ac,DAT_005713ac);
      }
      if (cVar1 == '\0') {
        production_codec_mic_func_init(*(undefined1 *)(param_1 + 5));
      }
      else if (cVar1 == '\x01') {
        production_pdm_mic_func_init();
      }
      else if (cVar1 == '\x02') {
        FUN_0053a5be(0x86,1);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_20 = (undefined1 *)0x86;
          local_24 = DAT_005713b0;
          local_28 = 0x56e;
          FUN_0043d574(3,DAT_00571054,DAT_00571050,DAT_005713a0);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_005713b4,DAT_005713b4,0x86);
        }
      }
      else {
        if (cVar1 != '\x03') {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            local_20 = DAT_005713a0;
            local_24 = DAT_005713bc;
            local_28 = 0x57d;
            FUN_0043d574(1,DAT_00571054,DAT_00571050);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_005713c0,DAT_005713c0,DAT_005713a0);
          }
          param_3[4] = 3;
          param_3[5] = cVar1;
          *param_4 = 6;
          return 0;
        }
        local_28 = *DAT_005713b8;
        local_24 = DAT_005713b8[1];
        local_20 = (undefined1 *)DAT_005713b8[2];
        uVar3 = FUN_0045a568();
        local_24 = CONCAT31(local_24._1_3_,uVar3);
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          uVar3 = 2;
        }
        else {
          uVar3 = 1;
        }
        local_24._0_2_ = CONCAT11(uVar3,(undefined1)local_24);
        FUN_004651e0(0x102,&local_28,0xc,0);
      }
      param_3[4] = 0;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_24 = DAT_00571380;
        local_28 = 0x588;
        FUN_0043d574(1,DAT_00571054,DAT_00571050,DAT_005713a0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00571384,DAT_00571384);
      }
      param_3[4] = 5;
    }
    param_3[5] = cVar1;
    *param_4 = 6;
    uVar5 = 0;
  }
  return uVar5;
}

