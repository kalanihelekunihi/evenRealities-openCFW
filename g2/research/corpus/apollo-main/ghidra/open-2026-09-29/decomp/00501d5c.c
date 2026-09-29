
undefined4 FUN_00501d5c(void)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined *puVar5;
  undefined *puVar6;
  undefined4 in_r3;
  undefined *local_48;
  uint local_44;
  undefined *local_40;
  undefined *local_3c;
  uint local_38;
  int local_34;
  int local_30;
  undefined1 auStack_2c [12];
  undefined *local_20;
  undefined4 uStack_1c;
  
  puVar1 = DAT_0050215c;
  *DAT_0050215c = 0;
  uStack_1c = in_r3;
  iVar2 = FUN_0055876a();
  puVar5 = DAT_0050261c;
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_40 = DAT_0050261c;
      local_44 = DAT_00502620;
      local_48 = (undefined *)0x315;
      FUN_0043d574(2,DAT_0050262c,DAT_00502628,DAT_00502624);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00502630,DAT_00502630,DAT_0050261c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = file_open(DAT_0050261c,&LAB_005020ec);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_40 = puVar5;
        local_44 = DAT_00502634;
        local_48 = (undefined *)0x31a;
        FUN_0043d574(1,DAT_0050262c,DAT_00502628,DAT_00502624);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00502638,DAT_00502638,puVar5);
      }
      uVar3 = 0xffffffff;
    }
    else {
      iVar4 = file_seek(iVar2,0,2);
      if (iVar4 == 0) {
        puVar5 = (undefined *)file_tell(iVar2);
        if (puVar5 + -1 < (undefined *)0x1000) {
          iVar4 = file_seek(iVar2,0,0);
          uVar3 = DAT_00502654;
          if (iVar4 == 0) {
            FUN_0043c0e4(DAT_00502654,0x1000,0);
            puVar6 = (undefined *)file_read(uVar3,1,puVar5,iVar2);
            file_close(iVar2);
            iVar2 = DAT_00502660;
            if (puVar6 == puVar5) {
              FUN_0043c0e4(DAT_00502660,0xbc,0);
              FUN_0048f49c(&local_48,uVar3,puVar5);
              FUN_00439c04(auStack_2c,&local_48,0x10);
              iVar4 = FUN_00490120(auStack_2c,DAT_00502664,iVar2);
              if (iVar4 == 0) {
                iVar2 = FUN_0043d0ce();
                if (iVar2 << 0x1e < 0) {
                  local_40 = PTR_s__none__005025e8;
                  if (local_20 != (undefined *)0x0) {
                    local_40 = local_20;
                  }
                  local_44 = DAT_00502668;
                  local_48 = (undefined *)0x342;
                  FUN_0043d574(1,DAT_0050262c,DAT_00502628,DAT_00502624);
                }
                iVar2 = FUN_0043d0ce();
                if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                  puVar5 = PTR_s__none__005025e8;
                  if (local_20 != (undefined *)0x0) {
                    puVar5 = local_20;
                  }
                  compress_log_output(0x4400000,DAT_0050266c,DAT_0050266c,puVar5);
                }
                uVar3 = 0xffffffff;
              }
              else {
                *puVar1 = 1;
                iVar4 = FUN_0043d0ce();
                if (iVar4 << 0x1e < 0) {
                  local_30 = iVar2 + 0x10;
                  local_34 = iVar2;
                  local_38 = (uint)*(ushort *)(iVar2 + 0x38);
                  local_3c = *(undefined **)(iVar2 + 0x34);
                  local_40 = (undefined *)(uint)*(byte *)(iVar2 + 0x30);
                  local_44 = DAT_00502670;
                  local_48 = (undefined *)0x34c;
                  FUN_0043d574(3,DAT_0050262c,DAT_00502628,DAT_00502624);
                }
                iVar4 = FUN_0043d0ce();
                if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                  local_3c = (undefined *)(iVar2 + 0x10);
                  local_40 = (undefined *)iVar2;
                  local_44 = (uint)*(ushort *)(iVar2 + 0x38);
                  local_48 = *(undefined **)(iVar2 + 0x34);
                  compress_log_output(0xd400000,DAT_00502674,DAT_00502674,
                                      *(undefined1 *)(iVar2 + 0x30));
                }
                uVar3 = 0;
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                local_44 = DAT_00502658;
                local_48 = (undefined *)0x337;
                local_40 = puVar5;
                local_3c = puVar6;
                FUN_0043d574(1,DAT_0050262c,DAT_00502628,DAT_00502624);
              }
              iVar2 = FUN_0043d0ce();
              if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                local_48 = puVar6;
                compress_log_output(0x4800000,DAT_0050265c,DAT_0050265c,puVar5);
              }
              uVar3 = 0xffffffff;
            }
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_44 = DAT_0050264c;
              local_48 = (undefined *)0x32b;
              FUN_0043d574(1,DAT_0050262c,DAT_00502628,DAT_00502624);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x4000000,DAT_00502650,DAT_00502650);
            }
            file_close(iVar2);
            uVar3 = 0xffffffff;
          }
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            local_3c = (undefined *)0x1000;
            local_44 = DAT_00502644;
            local_48 = (undefined *)0x326;
            local_40 = puVar5;
            FUN_0043d574(1,DAT_0050262c,DAT_00502628,DAT_00502624);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            local_48 = (undefined *)0x1000;
            compress_log_output(0x4800000,DAT_00502648,DAT_00502648,puVar5);
          }
          file_close(iVar2);
          uVar3 = 0xffffffff;
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_44 = DAT_0050263c;
          local_48 = (undefined *)0x31f;
          FUN_0043d574(1,DAT_0050262c,DAT_00502628,DAT_00502624);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00502640,DAT_00502640);
        }
        file_close(iVar2);
        uVar3 = 0xffffffff;
      }
    }
  }
  return uVar3;
}

