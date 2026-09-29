
undefined4 FUN_0058ca2a(undefined1 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 local_48;
  undefined4 local_44;
  uint local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  uint local_24;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  if (param_2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_44 = DAT_0058d424;
      local_48 = 0x85;
      FUN_0043d574(1,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058d42c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    bVar1 = FUN_005540b2();
    if (bVar1 == 0) {
      iVar2 = FUN_0045a568();
      if (iVar2 == 1) {
        local_48 = *DAT_0058d430;
        local_44 = DAT_0058d430[1];
        FUN_0048eb32(DAT_0058d434,2,&local_48);
      }
      iVar2 = FUN_0045a568();
      if (iVar2 == 1) {
        FUN_0045a8ee(6,0,0,500);
      }
    }
    else {
      if (bVar1 != 1) {
        if (bVar1 == 2) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            local_44 = DAT_0058d478;
            local_48 = 0x96;
            FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0058d47c,DAT_0058d47c);
          }
          return 0;
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_3c = FUN_005540bc(bVar1);
          local_40 = (uint)bVar1;
          local_44 = DAT_0058d480;
          local_48 = 0x99;
          FUN_0043d574(1,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          local_48 = FUN_005540bc(bVar1);
          compress_log_output(0x4800000,PTR_s__teleprompt_fsm_teleprompt_ui_st_0058d484,
                              PTR_s__teleprompt_fsm_teleprompt_ui_st_0058d484,bVar1);
        }
        return 0xffffffff;
      }
      FUN_00589b68(2,0);
    }
    *param_1 = 1;
    FUN_0058c882();
    if ((param_2 != 0) && (*(char *)(param_2 + 1) != '\0')) {
      FUN_00439be4(param_1 + 4,param_2 + 4,0x2c);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_18 = (uint)(byte)param_1[0x2c];
        local_1c = *(undefined4 *)(param_1 + 0x28);
        local_20 = *(undefined4 *)(param_1 + 0x24);
        local_24 = *(uint *)(param_1 + 0x20);
        local_28 = *(undefined4 *)(param_1 + 0x1c);
        local_2c = *(undefined4 *)(param_1 + 0x18);
        local_30 = *(undefined4 *)(param_1 + 0x14);
        local_34 = *(undefined4 *)(param_1 + 0x10);
        local_38 = *(undefined4 *)(param_1 + 0xc);
        local_3c = *(undefined4 *)(param_1 + 8);
        local_40 = (uint)(byte)param_1[4];
        local_44 = DAT_0058d438;
        local_48 = 0xaa;
        FUN_0043d574(3,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        local_24 = (uint)(byte)param_1[0x2c];
        local_28 = *(undefined4 *)(param_1 + 0x28);
        local_2c = *(undefined4 *)(param_1 + 0x24);
        local_30 = *(undefined4 *)(param_1 + 0x20);
        local_34 = *(undefined4 *)(param_1 + 0x1c);
        local_38 = *(undefined4 *)(param_1 + 0x18);
        local_3c = *(undefined4 *)(param_1 + 0x14);
        local_40 = *(uint *)(param_1 + 0x10);
        local_44 = *(undefined4 *)(param_1 + 0xc);
        local_48 = *(undefined4 *)(param_1 + 8);
        compress_log_output(((byte)param_1[0x2c] & 0xf) << 0x16 | 0xc000000,DAT_0058d43c,
                            DAT_0058d43c,param_1[4]);
      }
    }
    if (2 < (byte)param_1[4]) {
      param_1[4] = 1;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_40 = (uint)(byte)param_1[4];
        local_44 = DAT_0058d440;
        local_48 = 0xb0;
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058d444,DAT_0058d444,param_1[4]);
      }
    }
    if (*(int *)(param_1 + 0x10) - 1U < *(uint *)(param_1 + 8)) {
      *(undefined4 *)(param_1 + 8) = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_40 = *(uint *)(param_1 + 8);
        local_44 = DAT_0058d448;
        local_48 = 0xb5;
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058d44c,DAT_0058d44c,*(undefined4 *)(param_1 + 8));
      }
    }
    if (0x1e < *(uint *)(param_1 + 0xc)) {
      *(undefined4 *)(param_1 + 0xc) = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_40 = *(uint *)(param_1 + 0xc);
        local_44 = DAT_0058d450;
        local_48 = 0xba;
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058d454,DAT_0058d454,*(undefined4 *)(param_1 + 0xc));
      }
    }
    if (*(int *)(param_1 + 0x18) == 0) {
      *(undefined4 *)(param_1 + 0x18) = 0x237;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_40 = *(uint *)(param_1 + 0x18);
        local_44 = DAT_0058d458;
        local_48 = 0xbf;
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058d45c,DAT_0058d45c,*(undefined4 *)(param_1 + 0x18));
      }
    }
    if (4 < *(int *)(param_1 + 0x28) - 5U) {
      *(undefined4 *)(param_1 + 0x28) = 5;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_40 = *(uint *)(param_1 + 0x28);
        local_44 = DAT_0058d460;
        local_48 = 0xc5;
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058d464,DAT_0058d464,*(undefined4 *)(param_1 + 0x28));
      }
    }
    if (2 < (byte)param_1[0x2c]) {
      param_1[0x2c] = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_40 = (uint)(byte)param_1[0x2c];
        local_44 = DAT_0058d468;
        local_48 = 0xcb;
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058d46c,DAT_0058d46c,param_1[0x2c]);
      }
    }
    if (*(uint *)(param_1 + 0x1c) < 800) {
      *(undefined4 *)(param_1 + 0x1c) = 800;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_40 = *(uint *)(param_1 + 0x1c);
        local_44 = DAT_0058d470;
        local_48 = 0xd0;
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d428);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058d474,DAT_0058d474,*(undefined4 *)(param_1 + 0x1c));
      }
    }
    if (*(int *)(param_1 + 0x24) != 0) {
      AUDM_appAcquire(2);
    }
    uVar3 = 0;
  }
  return uVar3;
}

