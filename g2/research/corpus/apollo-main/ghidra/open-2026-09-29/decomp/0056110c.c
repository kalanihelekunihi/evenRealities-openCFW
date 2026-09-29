
void TouchUpdateFirmwareCheck(char param_1)

{
  int iVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 local_68;
  undefined4 local_64;
  undefined1 *local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined1 auStack_50 [32];
  undefined1 auStack_30 [32];
  
  local_54 = 0;
  local_58 = 0;
  FUN_0043c0e4(auStack_30,0x20,0);
  FUN_0043c0e4(auStack_50,0x20,0);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    local_64 = DAT_00561764;
    local_68 = 0x377;
    FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00561774,DAT_00561774);
  }
  FUN_0055b64a();
  puVar2 = (undefined1 *)FUN_0055b6dc(&local_54);
  if (puVar2 != (undefined1 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_64 = DAT_00561778;
      local_68 = 0x37e;
      local_60 = puVar2;
      FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0056177c,DAT_0056177c,puVar2);
    }
    param_1 = '\x01';
  }
  semantic_TouchFormatVersion(local_54,auStack_50,0x20);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    local_5c = local_54;
    local_60 = auStack_50;
    local_64 = DAT_00561780;
    local_68 = 0x382;
    FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    local_68 = local_54;
    compress_log_output(0xc800000,DAT_00561784,DAT_00561784,auStack_50);
  }
  puVar2 = (undefined1 *)get_touch_firmware_package_version(&local_58);
  if (puVar2 == (undefined1 *)0x0) {
    semantic_TouchFormatVersion(local_58,auStack_30,0x20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_5c = local_58;
      local_60 = auStack_30;
      local_64 = DAT_00561790;
      local_68 = 0x38b;
      FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_68 = local_58;
      compress_log_output(0xc800000,DAT_00561794,DAT_00561794,auStack_30);
    }
    if (param_1 == '\0') {
      iVar1 = isTouchNeedUpgrade(local_54,local_58);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_64 = DAT_00561798;
          local_68 = 0x390;
          FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
        }
        iVar1 = FUN_0043d0ce();
        if ((-1 < iVar1 << 0x1f) && (iVar1 = FUN_0043d0ce(), -1 < iVar1 << 0x1d)) {
          return;
        }
        compress_log_output(0xc000000,DAT_0056179c,DAT_0056179c);
        return;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_64 = DAT_005617a0;
        local_68 = 0x394;
        FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_005617a4,DAT_005617a4);
      }
    }
    puVar2 = (undefined1 *)load_touch_firmware_from_package();
    if (puVar2 == (undefined1 *)0x0) {
      uVar3 = *DAT_005617b0;
      uVar4 = *DAT_005617b4;
      puVar2 = (undefined1 *)FUN_0055b5e4();
      if (puVar2 == (undefined1 *)0x0) {
        osDelay(0x32);
        puVar2 = (undefined1 *)TouchEnterDFU();
        if (puVar2 == (undefined1 *)0x0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            local_64 = DAT_005617c8;
            local_68 = 0x3b1;
            FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_005617cc,DAT_005617cc);
          }
          puVar2 = (undefined1 *)TouchSetAppMeta(uVar4);
          if (puVar2 == (undefined1 *)0x0) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              local_64 = DAT_005617d8;
              local_68 = 0x3bb;
              FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_005617dc,DAT_005617dc);
            }
            puVar2 = (undefined1 *)TouchSendAppFile(uVar3,uVar4);
            if (puVar2 == (undefined1 *)0x0) {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                local_64 = DAT_005617e8;
                local_68 = 0x3c5;
                FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0xc000000,DAT_005617ec,DAT_005617ec);
              }
              puVar2 = (undefined1 *)TouchVerifyApp();
              if (puVar2 == (undefined1 *)0x0) {
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  local_64 = DAT_005617f8;
                  local_68 = 0x3cf;
                  FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
                }
                iVar1 = FUN_0043d0ce();
                if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                  compress_log_output(0xc000000,DAT_005617fc,DAT_005617fc);
                }
                puVar2 = (undefined1 *)TouchExitDFU();
                if (puVar2 == (undefined1 *)0x0) {
                  iVar1 = FUN_0043d0ce();
                  if (iVar1 << 0x1e < 0) {
                    local_64 = DAT_00561808;
                    local_68 = 0x3d9;
                    FUN_0043d574(3,DAT_00561770,DAT_0056176c,DAT_00561768);
                  }
                  iVar1 = FUN_0043d0ce();
                  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                    compress_log_output(0xc000000,DAT_0056180c,DAT_0056180c);
                  }
                  osDelay(500);
                  local_68 = 0;
                  FUN_0055b6dc(&local_68);
                  free_touch_firmware_memory();
                }
                else {
                  iVar1 = FUN_0043d0ce();
                  if (iVar1 << 0x1e < 0) {
                    local_64 = DAT_00561800;
                    local_68 = 0x3d5;
                    local_60 = puVar2;
                    FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
                  }
                  iVar1 = FUN_0043d0ce();
                  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                    compress_log_output(0x4400000,DAT_00561804,DAT_00561804,puVar2);
                  }
                  free_touch_firmware_memory();
                }
              }
              else {
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  local_64 = DAT_005617f0;
                  local_68 = 0x3cb;
                  local_60 = puVar2;
                  FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
                }
                iVar1 = FUN_0043d0ce();
                if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                  compress_log_output(0x4400000,DAT_005617f4,DAT_005617f4,puVar2);
                }
                free_touch_firmware_memory();
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                local_64 = DAT_005617e0;
                local_68 = 0x3c1;
                local_60 = puVar2;
                FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x4400000,DAT_005617e4,DAT_005617e4,puVar2);
              }
              free_touch_firmware_memory();
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              local_64 = DAT_005617d0;
              local_68 = 0x3b7;
              local_60 = puVar2;
              FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_005617d4,DAT_005617d4,puVar2);
            }
            free_touch_firmware_memory();
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            local_64 = DAT_005617c0;
            local_68 = 0x3ad;
            local_60 = puVar2;
            FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_005617c4,DAT_005617c4,puVar2);
          }
          free_touch_firmware_memory();
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_64 = DAT_005617b8;
          local_68 = 0x3a5;
          local_60 = puVar2;
          FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_005617bc,DAT_005617bc,puVar2);
        }
        free_touch_firmware_memory();
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_64 = DAT_005617a8;
        local_68 = 0x39a;
        local_60 = puVar2;
        FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005617ac,DAT_005617ac,puVar2);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_64 = DAT_00561788;
      local_68 = 0x387;
      local_60 = puVar2;
      FUN_0043d574(1,DAT_00561770,DAT_0056176c,DAT_00561768);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0056178c,DAT_0056178c,puVar2);
    }
  }
  return;
}

