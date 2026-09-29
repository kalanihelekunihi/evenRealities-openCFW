
int tracepoint_handle_slave_file_list(int param_1,undefined1 *param_2)

{
  int *piVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  undefined *puVar5;
  undefined1 *puVar6;
  uint uVar7;
  uint uVar8;
  uint local_240;
  undefined4 local_23c;
  undefined1 *local_238;
  uint local_234;
  undefined1 auStack_230 [12];
  undefined1 *local_224;
  byte local_220 [2];
  ushort local_21e;
  ushort local_21c;
  undefined1 auStack_21a [514];
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    local_23c = DAT_005ef054;
    local_240 = 0x1df;
    local_238 = param_2;
    FUN_0043d574(4,DAT_005ef018,DAT_005ef014,DAT_005ef058);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005ef05c,DAT_005ef05c,param_2);
  }
  if ((param_1 == 0) || (param_2 == (undefined1 *)0x0)) {
    iVar3 = -1;
  }
  else {
    FUN_0043c0e4(local_220,0x206,0);
    FUN_0048f49c(&local_240,param_1,param_2);
    FUN_00439c04(auStack_230,&local_240,0x10);
    cVar2 = FUN_00490120(auStack_230,DAT_005ef024,local_220);
    iVar3 = DAT_005ef078;
    piVar1 = DAT_005eefac;
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_238 = PTR_s__none__005ef028;
        if (local_224 != (undefined1 *)0x0) {
          local_238 = local_224;
        }
        local_23c = DAT_005ef060;
        local_240 = 0x1ed;
        FUN_0043d574(1,DAT_005ef018,DAT_005ef014,DAT_005ef058);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        puVar5 = PTR_s__none__005ef028;
        if (local_224 != (undefined1 *)0x0) {
          puVar5 = local_224;
        }
        compress_log_output(0x4400000,DAT_005ef064,DAT_005ef064,puVar5);
      }
      iVar3 = -1;
    }
    else if ((local_220[0] == 1) && (local_21e == 3)) {
      if (*DAT_005eefac == 1) {
        puVar6 = (undefined1 *)(uint)*(ushort *)(DAT_005ef078 + 4);
        uVar7 = (uint)local_21c;
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_23c = DAT_005ef07c;
          local_240 = 0x200;
          local_238 = puVar6;
          local_234 = uVar7;
          FUN_0043d574(4,DAT_005ef018,DAT_005ef014,DAT_005ef058);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          local_240 = uVar7;
          compress_log_output(0x10800000,DAT_005ef080,DAT_005ef080,puVar6);
        }
        uVar8 = 0;
        for (; (uVar8 < uVar7 && (puVar6 < &MemManage)); puVar6 = puVar6 + 1) {
          FUN_0044b5a0((int)puVar6 * 0x20 + iVar3 + 6,auStack_21a + uVar8 * 0x20,0x1f);
          *(undefined1 *)((int)puVar6 * 0x20 + iVar3 + 0x25) = 0;
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            local_234 = (int)puVar6 * 0x20 + iVar3 + 6;
            local_23c = DAT_005ef084;
            local_240 = 0x209;
            local_238 = puVar6;
            FUN_0043d574(4,DAT_005ef018,DAT_005ef014,DAT_005ef058);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            local_240 = (int)puVar6 * 0x20 + iVar3 + 6;
            compress_log_output(0x10800000,DAT_005ef088,DAT_005ef088,puVar6);
          }
          uVar8 = uVar8 + 1;
        }
        *(short *)(iVar3 + 4) = (short)puVar6;
        iVar3 = tracepoint_send_to_phone(iVar3);
        if (iVar3 == 0) {
          *piVar1 = 0;
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_23c = DAT_005ef094;
            local_240 = 0x217;
            local_238 = puVar6;
            FUN_0043d574(4,DAT_005ef018,DAT_005ef014,DAT_005ef058);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__tp_setting_tracepoint_send_merg_005ef098,
                                PTR_s__tp_setting_tracepoint_send_merg_005ef098,puVar6);
          }
          iVar3 = 0;
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            local_23c = DAT_005ef08c;
            local_240 = 0x211;
            FUN_0043d574(1,DAT_005ef018,DAT_005ef014,DAT_005ef058);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_005ef090,DAT_005ef090);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_23c = DAT_005ef070;
          local_240 = 0x1f9;
          FUN_0043d574(2,DAT_005ef018,DAT_005ef014,DAT_005ef058);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_005ef074,DAT_005ef074);
        }
        iVar3 = 0;
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_234 = (uint)local_21e;
        local_238 = (undefined1 *)(uint)local_220[0];
        local_23c = DAT_005ef068;
        local_240 = 500;
        FUN_0043d574(2,DAT_005ef018,DAT_005ef014,DAT_005ef058);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        local_240 = (uint)local_21e;
        compress_log_output(0x8800000,DAT_005ef06c,DAT_005ef06c,local_220[0]);
      }
      iVar3 = 0;
    }
  }
  return iVar3;
}

