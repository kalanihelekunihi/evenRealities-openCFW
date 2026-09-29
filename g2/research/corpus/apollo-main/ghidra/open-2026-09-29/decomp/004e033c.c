
undefined4 FUN_004e033c(int *param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  undefined4 local_28;
  uint local_24;
  undefined4 local_20;
  uint local_1c;
  undefined4 uStack_18;
  undefined1 uVar2;
  
  uStack_18 = param_4;
  if (param_1 == (int *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2ba,DAT_004e0b60);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004e0b68,DAT_004e0b68);
    }
    uVar4 = 0xffffffff;
  }
  else if ((*param_1 == 0) || (param_1[1] == 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2bf,DAT_004e0b6c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004e0b70,DAT_004e0b70);
    }
    uVar4 = 0xffffffff;
  }
  else if (((param_2 == 0) || (param_2 == 1)) || (param_2 == 2)) {
    if (*(char *)((int)param_1 + 0x13) == '\0') {
      FUN_004df858(param_1);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_1c = (uint)*(byte *)((int)param_1 + 0x11);
        local_20 = (uint)*(byte *)(param_1 + 4);
        local_24 = (uint)*(byte *)((int)param_1 + 0x12);
        local_28 = (uint)param_2;
        FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2fa,DAT_004e0ba4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        local_28 = (uint)*(byte *)((int)param_1 + 0x11);
        compress_log_output(0x11000000,DAT_004e0ba8,DAT_004e0ba8,param_2,
                            *(undefined1 *)((int)param_1 + 0x12),(char)param_1[4]);
      }
      if (param_2 == 0) {
        if (*(char *)((int)param_1 + 0x12) == '\0') {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x32c,DAT_004e0bc4);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004e0bc8,DAT_004e0bc8);
          }
          if (param_1[0x208] != 0) {
            (*(code *)param_1[0x208])(0,param_1[0x209]);
          }
          FUN_004dfe50(param_1,0);
        }
        else if (*(char *)((int)param_1 + 0x11) == '\0') {
          iVar3 = FUN_004df97c(param_3,param_4);
          uVar5 = FUN_0044e498(*param_1);
          uVar6 = iVar3 + uVar5;
          if (param_1[3] < (int)uVar6) {
            uVar6 = param_1[3];
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_28 = uVar5;
            local_24 = uVar6;
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x34e,DAT_004e0bd4);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_004e0bd8,DAT_004e0bd8,uVar5,uVar6);
          }
          FUN_004dfb78(param_1,uVar6,200);
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x339,DAT_004e0bcc);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004e0bd0,DAT_004e0bd0);
          }
          if (param_1[0x208] != 0) {
            (*(code *)param_1[0x208])(0,param_1[0x209]);
          }
          FUN_004dfe50(param_1,0);
        }
      }
      else if (param_2 == 2) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x355,DAT_004e0bdc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e0be0,DAT_004e0be0);
        }
        if (param_1[2] == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x358,DAT_004e0be4);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004e0be8,DAT_004e0be8);
          }
          return 0xffffffff;
        }
        if ((char)param_1[8] == '\0') {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(2,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x35e,DAT_004e0bec);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_004e0bf0,DAT_004e0bf0);
          }
          return 0xffffffff;
        }
        FUN_0049942e(param_1[2],param_1 + 8);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_28 = FUN_0044a43c(param_1 + 8);
          FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x364,DAT_004e0bf4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          uVar4 = FUN_0044a43c(param_1 + 8);
          compress_log_output(0x10400000,DAT_004e0bf8,DAT_004e0bf8,uVar4);
        }
        FUN_0043f66c(*param_1);
        FUN_004df858(param_1);
        FUN_0044ea04(*param_1,0,0);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x36e,DAT_004e0bfc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e0c00,DAT_004e0c00);
        }
      }
      else {
        if (1 < param_2) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_28 = (uint)param_2;
            FUN_0043d574(2,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x374,DAT_004e0c04);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8400000,DAT_004e0c08,DAT_004e0c08,param_2);
          }
          return 0xffffffff;
        }
        if (*(char *)((int)param_1 + 0x12) == '\0') {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x301,DAT_004e0bac);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004e0bb0,DAT_004e0bb0);
          }
          if (param_1[0x208] != 0) {
            (*(code *)param_1[0x208])(1,param_1[0x209]);
          }
          FUN_004dfe50(param_1,1);
        }
        else if ((char)param_1[4] == '\0') {
          iVar3 = FUN_004df97c(param_3,param_4);
          uVar5 = FUN_0044e498(*param_1);
          uVar6 = uVar5 - iVar3;
          if ((int)uVar6 < 0) {
            uVar6 = 0;
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_28 = uVar5;
            local_24 = uVar6;
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x323,DAT_004e0bbc);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_004e0bc0,DAT_004e0bc0,uVar5,uVar6);
          }
          FUN_004dfb78(param_1,uVar6,200);
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x30e,DAT_004e0bb4);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004e0bb8,DAT_004e0bb8);
          }
          if (param_1[0x208] != 0) {
            (*(code *)param_1[0x208])(1,param_1[0x209]);
          }
          FUN_004dfe50(param_1,1);
        }
      }
      uVar4 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2cd,DAT_004e0b7c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004e0b80,DAT_004e0b80);
      }
      uVar1 = (undefined1)((uint)param_3 >> 8);
      uVar2 = (undefined1)((uint)param_4 >> 8);
      if ((param_2 == 0) || (param_2 == 1)) {
        iVar3 = FUN_004dfff8(param_1,param_2,param_3,param_4);
        if (iVar3 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2d6,DAT_004e0b8c);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004e0b90,DAT_004e0b90);
          }
          local_20 = CONCAT13((char)param_4,CONCAT12(uVar1,CONCAT11((char)param_3,param_2)));
          local_1c = CONCAT31(local_1c._1_3_,uVar2);
          iVar3 = ui_common_api_fn_00509ca2(param_1[6],&local_20,5);
          if (iVar3 == 0) {
            uVar4 = 0;
          }
          else {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(2,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2de,DAT_004e0b94);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_004e0b98,DAT_004e0b98);
            }
            uVar4 = 0xffffffff;
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2d2,DAT_004e0b84);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004e0b88,DAT_004e0b88);
          }
          uVar4 = 0;
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2e5,DAT_004e0b9c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e0ba0,DAT_004e0ba0);
        }
        local_28 = CONCAT13((char)param_4,CONCAT12(uVar1,CONCAT11((char)param_3,param_2)));
        local_24 = CONCAT31(local_24._1_3_,uVar2);
        iVar3 = ui_common_api_fn_00509ca2(param_1[6],&local_28,5);
        if (iVar3 == 0) {
          uVar4 = 0;
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(2,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2ed,DAT_004e0b94);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_004e0b98,DAT_004e0b98);
          }
          uVar4 = 0xffffffff;
        }
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_28 = (uint)param_2;
      FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b64,0x2c7,DAT_004e0b74);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004e0b78,DAT_004e0b78,param_2);
    }
    uVar4 = 1;
  }
  return uVar4;
}

