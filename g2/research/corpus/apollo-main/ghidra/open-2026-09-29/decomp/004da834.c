
int FUN_004da834(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  ushort uVar2;
  char cVar3;
  short sVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  byte bVar8;
  uint *puVar9;
  byte *pbVar10;
  int iVar11;
  byte bVar12;
  byte *local_130;
  uint local_12c;
  uint local_128;
  byte *local_124;
  uint local_120;
  undefined4 local_11c;
  undefined4 local_118;
  undefined4 local_114;
  undefined4 local_110;
  undefined1 auStack_10c [12];
  uint local_100;
  undefined1 local_fc;
  undefined1 local_fb;
  undefined1 auStack_fa [218];
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  FUN_004d9b34();
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    local_12c = DAT_004db4b8;
    local_130 = (byte *)0x210;
    local_128 = param_2;
    FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004db4c8,DAT_004db4c8,param_2);
  }
  pbVar10 = DAT_004db4d4;
  if (param_2 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      local_12c = DAT_004db4cc;
      local_130 = (byte *)0x212;
      FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004db4d0,DAT_004db4d0);
    }
    iVar5 = -2;
  }
  else {
    FUN_0043c0e4(DAT_004db4d4,0x3758,0);
    FUN_0048f49c(&local_130,param_1,param_2);
    FUN_00439c04(auStack_10c,&local_130,0x10);
    cVar3 = FUN_00490120(auStack_10c,DAT_004db5cc,pbVar10);
    if (cVar3 == '\0') {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        local_128 = DAT_004db5d0;
        if (local_100 != 0) {
          local_128 = local_100;
        }
        local_12c = DAT_004db5d4;
        local_130 = (byte *)0x21a;
        FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        uVar7 = DAT_004db5d0;
        if (local_100 != 0) {
          uVar7 = local_100;
        }
        compress_log_output(0x4400000,DAT_004db5d8,DAT_004db5d8,uVar7);
      }
      iVar5 = -3;
    }
    else {
      bVar8 = *pbVar10;
      bVar1 = pbVar10[1];
      uVar2 = *(ushort *)(pbVar10 + 2);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        local_120 = (uint)uVar2;
        local_124 = (byte *)(uint)bVar1;
        local_128 = (uint)bVar8;
        local_12c = DAT_004db5dc;
        local_130 = (byte *)0x221;
        FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        local_12c = (uint)uVar2;
        local_130 = (byte *)(uint)bVar1;
        compress_log_output(0x10c00000,DAT_004db6a4,DAT_004db6a4,bVar8);
      }
      if (bVar8 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004db6a8;
          local_130 = (byte *)0x225;
          FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004db6ac,DAT_004db6ac);
        }
        if (uVar2 == 3) {
          puVar9 = (uint *)(pbVar10 + 4);
          if (*puVar9 < 0xd) {
            if ((uint)*(ushort *)(pbVar10 + 0x155c) + (uint)*(ushort *)(pbVar10 + 8) +
                (uint)*(ushort *)(pbVar10 + 0x36a0) < 0xd) {
              bVar12 = 0;
              for (bVar8 = 0; (ushort)bVar8 < *(ushort *)(pbVar10 + 8); bVar8 = bVar8 + 1) {
                if (puVar9[(uint)bVar8 * 0x155 + 0x154] == 1) {
                  bVar12 = bVar12 + 1;
                }
              }
              for (uVar7 = 0; (uVar7 & 0xff) < (uint)*(ushort *)(pbVar10 + 0x155c);
                  uVar7 = uVar7 + 1) {
                if (puVar9[(uVar7 & 0xff) * 0x10a + 0x564] == 1) {
                  bVar12 = bVar12 + 1;
                }
              }
              if (bVar12 < 2) {
                iVar5 = FUN_0045a568();
                if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 0)) {
                  uVar7 = FUN_00464b2e(0xe0,param_1,param_2 & 0xffff,0);
                  local_118 = *(undefined4 *)(DAT_004db84c + 4);
                  local_11c = *(undefined4 *)(pbVar10 + 0x3754);
                  FUN_0048eb32(DAT_004db850,2,&local_11c);
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    local_12c = DAT_004db854;
                    local_130 = (byte *)0x256;
                    local_128 = uVar7;
                    FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0x10400000,DAT_004db858,DAT_004db858,uVar7);
                  }
                }
                iVar5 = 0;
              }
              else {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  local_128 = (uint)bVar12;
                  local_12c = DAT_004db844;
                  local_130 = (byte *)0x24d;
                  FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x4400000,DAT_004db848,DAT_004db848,bVar12);
                }
                FUN_004d9c86(1,bVar1,4,1);
                iVar5 = -4;
              }
            }
            else {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                local_120 = (uint)*(ushort *)(pbVar10 + 0x36a0);
                local_124 = (byte *)(uint)*(ushort *)(pbVar10 + 0x155c);
                local_128 = (uint)*(ushort *)(pbVar10 + 8);
                local_12c = DAT_004db83c;
                local_130 = (byte *)0x237;
                FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                local_12c = (uint)*(ushort *)(pbVar10 + 0x36a0);
                local_130 = (byte *)(uint)*(ushort *)(pbVar10 + 0x155c);
                compress_log_output(0x4c00000,DAT_004db840,DAT_004db840,*(undefined2 *)(pbVar10 + 8)
                                   );
              }
              FUN_004d9c86(1,bVar1,4,2);
              iVar5 = -4;
            }
          }
          else {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              local_128 = *puVar9;
              local_12c = DAT_004db7b8;
              local_130 = (byte *)0x22f;
              FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_004db7bc,DAT_004db7bc,*puVar9);
            }
            FUN_004d9c86(1,bVar1,4,2);
            iVar5 = -4;
          }
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_128 = (uint)uVar2;
            local_12c = DAT_004db6b0;
            local_130 = (byte *)0x228;
            FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_004db6b4,DAT_004db6b4,uVar2);
          }
          iVar5 = -1;
        }
      }
      else if (bVar8 == 3) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004dbe44;
          local_130 = (byte *)0x2e7;
          FUN_0043d574(3,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004dbe48,DAT_004dbe48);
        }
        if (uVar2 == 5) {
          uVar7 = *(uint *)(pbVar10 + 4);
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_110 = *(undefined4 *)(pbVar10 + 0x28);
            local_114 = *(undefined4 *)(pbVar10 + 0x24);
            local_118 = *(undefined4 *)(pbVar10 + 0x20);
            local_11c = *(undefined4 *)(pbVar10 + 0x1c);
            local_120 = *(uint *)(pbVar10 + 0x18);
            local_124 = pbVar10 + 8;
            local_12c = DAT_004dbe54;
            local_130 = (byte *)0x2f7;
            local_128 = uVar7;
            FUN_0043d574(3,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            local_11c = *(undefined4 *)(pbVar10 + 0x28);
            local_120 = *(uint *)(pbVar10 + 0x24);
            local_124 = *(byte **)(pbVar10 + 0x20);
            local_128 = *(uint *)(pbVar10 + 0x1c);
            local_12c = *(uint *)(pbVar10 + 0x18);
            local_130 = pbVar10 + 8;
            compress_log_output(0xdc00000,DAT_004dbe58,DAT_004dbe58,uVar7);
          }
          iVar5 = FUN_004e0cce(uVar7);
          if (iVar5 == 0) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              local_12c = DAT_004dbe5c;
              local_130 = (byte *)0x2fb;
              local_128 = uVar7;
              FUN_0043d574(1,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_004dbe60,DAT_004dbe60,uVar7);
            }
            local_120 = *(uint *)(pbVar10 + 0x28);
            local_124 = *(byte **)(pbVar10 + 0x24);
            local_128 = *(uint *)(pbVar10 + 0x20);
            local_12c = *(uint *)(pbVar10 + 0x1c);
            local_130 = *(byte **)(pbVar10 + 0x18);
            FUN_004da4a4(bVar1,5,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
            iVar5 = -4;
          }
          else if (*(char *)(iVar5 + 8) == '\x02') {
            iVar11 = *(int *)(iVar5 + 0x10);
            if (*(int *)(iVar11 + 0x10) == 0) {
              if (*(int *)(pbVar10 + 0x24) == 0) {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  local_128 = *(uint *)(pbVar10 + 0x24);
                  local_12c = DAT_004dbe6c;
                  local_130 = (byte *)0x312;
                  FUN_0043d574(3,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0xc400000,DAT_004dbe70,DAT_004dbe70,
                                      *(undefined4 *)(pbVar10 + 0x24));
                }
                *(undefined4 *)(iVar11 + 0x10) = *(undefined4 *)(pbVar10 + 0x18);
                *(undefined4 *)(iVar11 + 0x14) = *(undefined4 *)(pbVar10 + 0x1c);
                *(undefined4 *)(iVar11 + 0x18) = *(undefined4 *)(pbVar10 + 0x20);
                *(undefined4 *)(iVar11 + 0x1c) = *(undefined4 *)(pbVar10 + 0x24);
                *(undefined4 *)(iVar11 + 0x20) = *(undefined4 *)(pbVar10 + 0x28);
                FUN_00439be4(*(undefined4 *)(iVar11 + 0xc),pbVar10 + 0x2e,
                             *(undefined4 *)(pbVar10 + 0x28));
                local_120 = *(uint *)(pbVar10 + 0x28);
                local_124 = *(byte **)(pbVar10 + 0x24);
                local_128 = *(uint *)(pbVar10 + 0x20);
                local_12c = *(uint *)(pbVar10 + 0x1c);
                local_130 = *(byte **)(pbVar10 + 0x18);
                FUN_004da4a4(bVar1,4,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
                iVar5 = *(int *)(iVar11 + 0x20);
                if (iVar5 == *(int *)(iVar11 + 0x14)) {
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    local_128 = *(uint *)(pbVar10 + 0x24);
                    local_12c = DAT_004dbe74;
                    local_130 = (byte *)0x31f;
                    FUN_0043d574(3,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0xc400000,DAT_004dbe78,DAT_004dbe78,
                                        *(undefined4 *)(pbVar10 + 0x24));
                  }
                  *(undefined4 *)(iVar11 + 0x10) = 0;
                  iVar5 = FUN_0045a568();
                  if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 1)) {
                    iVar5 = FUN_004da382(uVar7,pbVar10 + 8,0x4c,0);
                  }
                }
              }
              else {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  local_128 = *(uint *)(pbVar10 + 0x24);
                  local_12c = DAT_004dbe7c;
                  local_130 = (byte *)0x328;
                  FUN_0043d574(2,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x8400000,DAT_004dbe80,DAT_004dbe80,
                                      *(undefined4 *)(pbVar10 + 0x24));
                }
                *(undefined4 *)(iVar11 + 0x10) = 0;
                local_120 = *(uint *)(pbVar10 + 0x28);
                local_124 = *(byte **)(pbVar10 + 0x24);
                local_128 = *(uint *)(pbVar10 + 0x20);
                local_12c = *(uint *)(pbVar10 + 0x1c);
                local_130 = *(byte **)(pbVar10 + 0x18);
                iVar5 = FUN_004da4a4(bVar1,5,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
              }
            }
            else if (*(int *)(iVar11 + 0x10) == *(int *)(pbVar10 + 0x18)) {
              if (((*(int *)(iVar11 + 0x1c) == *(int *)(pbVar10 + 0x24) + -1) &&
                  (*(int *)(iVar11 + 0x14) == *(int *)(pbVar10 + 0x1c))) &&
                 (*(int *)(iVar11 + 0x18) == *(int *)(pbVar10 + 0x20))) {
                if (*(uint *)(iVar11 + 0x14) <
                    (uint)(*(int *)(pbVar10 + 0x28) + *(int *)(iVar11 + 0x20))) {
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    local_124 = *(byte **)(iVar11 + 0x14);
                    local_128 = *(uint *)(iVar11 + 0x20);
                    local_12c = DAT_004dbe9c;
                    local_130 = (byte *)0x357;
                    FUN_0043d574(1,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    local_130 = *(byte **)(iVar11 + 0x14);
                    compress_log_output(0x4800000,DAT_004dbea0,DAT_004dbea0,
                                        *(undefined4 *)(iVar11 + 0x20));
                  }
                  *(undefined4 *)(iVar11 + 0x10) = 0;
                  local_120 = *(uint *)(pbVar10 + 0x28);
                  local_124 = *(byte **)(pbVar10 + 0x24);
                  local_128 = *(uint *)(pbVar10 + 0x20);
                  local_12c = *(uint *)(pbVar10 + 0x1c);
                  local_130 = *(byte **)(pbVar10 + 0x18);
                  FUN_004da4a4(bVar1,5,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
                  iVar5 = -4;
                }
                else {
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    local_128 = *(uint *)(pbVar10 + 0x24);
                    local_12c = DAT_004dbe74;
                    local_130 = (byte *)0x360;
                    FUN_0043d574(3,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0xc400000,DAT_004dbe78,DAT_004dbe78,
                                        *(undefined4 *)(pbVar10 + 0x24));
                  }
                  *(undefined4 *)(iVar11 + 0x1c) = *(undefined4 *)(pbVar10 + 0x24);
                  FUN_00439be4(*(int *)(iVar11 + 0xc) + *(int *)(iVar11 + 0x20),pbVar10 + 0x2e,
                               *(undefined4 *)(pbVar10 + 0x28));
                  *(int *)(iVar11 + 0x20) = *(int *)(pbVar10 + 0x28) + *(int *)(iVar11 + 0x20);
                  local_120 = *(uint *)(pbVar10 + 0x28);
                  local_124 = *(byte **)(pbVar10 + 0x24);
                  local_128 = *(uint *)(pbVar10 + 0x20);
                  local_12c = *(uint *)(pbVar10 + 0x1c);
                  local_130 = *(byte **)(pbVar10 + 0x18);
                  FUN_004da4a4(bVar1,4,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
                  iVar5 = *(int *)(iVar11 + 0x20);
                  if (iVar5 == *(int *)(iVar11 + 0x14)) {
                    iVar5 = FUN_0043d0ce();
                    if (iVar5 << 0x1e < 0) {
                      local_128 = *(uint *)(pbVar10 + 0x24);
                      local_12c = DAT_004dbe74;
                      local_130 = (byte *)0x36a;
                      FUN_0043d574(3,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                    }
                    iVar5 = FUN_0043d0ce();
                    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                      compress_log_output(0xc400000,DAT_004dbe78,DAT_004dbe78,
                                          *(undefined4 *)(pbVar10 + 0x24));
                    }
                    *(undefined4 *)(iVar11 + 0x10) = 0;
                    iVar5 = FUN_0045a568();
                    if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 1)) {
                      iVar5 = FUN_004da382(uVar7,pbVar10 + 8,0x4c,0);
                    }
                  }
                }
              }
              else {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  local_124 = *(byte **)(pbVar10 + 0x24);
                  local_128 = *(uint *)(iVar11 + 0x1c);
                  local_12c = DAT_004dbe94;
                  local_130 = (byte *)0x34c;
                  FUN_0043d574(2,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  local_130 = *(byte **)(pbVar10 + 0x24);
                  compress_log_output(0x8800000,DAT_004dbe98,DAT_004dbe98,
                                      *(undefined4 *)(iVar11 + 0x1c));
                }
                *(undefined4 *)(iVar11 + 0x10) = 0;
                local_120 = *(uint *)(pbVar10 + 0x28);
                local_124 = *(byte **)(pbVar10 + 0x24);
                local_128 = *(uint *)(pbVar10 + 0x20);
                local_12c = *(uint *)(pbVar10 + 0x1c);
                local_130 = *(byte **)(pbVar10 + 0x18);
                FUN_004da4a4(bVar1,5,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
                iVar5 = -4;
              }
            }
            else {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                local_124 = *(byte **)(pbVar10 + 0x18);
                local_128 = *(uint *)(iVar11 + 0x10);
                local_12c = DAT_004dbe84;
                local_130 = (byte *)0x333;
                FUN_0043d574(2,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                local_130 = *(byte **)(pbVar10 + 0x18);
                compress_log_output(0x8800000,DAT_004dbe88,DAT_004dbe88,
                                    *(undefined4 *)(iVar11 + 0x10));
              }
              if (*(int *)(pbVar10 + 0x24) == 0) {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  local_12c = DAT_004dbe8c;
                  local_130 = (byte *)0x335;
                  FUN_0043d574(3,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0xc000000,DAT_004dbe90,DAT_004dbe90);
                }
                *(undefined4 *)(iVar11 + 0x10) = *(undefined4 *)(pbVar10 + 0x18);
                *(undefined4 *)(iVar11 + 0x14) = *(undefined4 *)(pbVar10 + 0x1c);
                *(undefined4 *)(iVar11 + 0x18) = *(undefined4 *)(pbVar10 + 0x20);
                *(undefined4 *)(iVar11 + 0x1c) = *(undefined4 *)(pbVar10 + 0x24);
                *(undefined4 *)(iVar11 + 0x20) = *(undefined4 *)(pbVar10 + 0x28);
                FUN_00439be4(*(undefined4 *)(iVar11 + 0xc),pbVar10 + 0x2e,
                             *(undefined4 *)(pbVar10 + 0x28));
                local_120 = *(uint *)(pbVar10 + 0x28);
                local_124 = *(byte **)(pbVar10 + 0x24);
                local_128 = *(uint *)(pbVar10 + 0x20);
                local_12c = *(uint *)(pbVar10 + 0x1c);
                local_130 = *(byte **)(pbVar10 + 0x18);
                iVar5 = FUN_004da4a4(bVar1,4,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
              }
              else {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  local_128 = *(uint *)(pbVar10 + 0x24);
                  local_12c = DAT_004dbe7c;
                  local_130 = (byte *)0x342;
                  FUN_0043d574(2,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x8400000,DAT_004dbe80,DAT_004dbe80,
                                      *(undefined4 *)(pbVar10 + 0x24));
                }
                *(undefined4 *)(iVar11 + 0x10) = 0;
                local_120 = *(uint *)(pbVar10 + 0x28);
                local_124 = *(byte **)(pbVar10 + 0x24);
                local_128 = *(uint *)(pbVar10 + 0x20);
                local_12c = *(uint *)(pbVar10 + 0x1c);
                local_130 = *(byte **)(pbVar10 + 0x18);
                iVar5 = FUN_004da4a4(bVar1,5,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
              }
            }
          }
          else {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              local_12c = DAT_004dbe64;
              local_130 = (byte *)0x305;
              local_128 = uVar7;
              FUN_0043d574(1,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_004dbe68,DAT_004dbe68,uVar7);
            }
            local_120 = *(uint *)(pbVar10 + 0x28);
            local_124 = *(byte **)(pbVar10 + 0x24);
            local_128 = *(uint *)(pbVar10 + 0x20);
            local_12c = *(uint *)(pbVar10 + 0x1c);
            local_130 = *(byte **)(pbVar10 + 0x18);
            FUN_004da4a4(bVar1,5,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
            iVar5 = -4;
          }
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_128 = (uint)uVar2;
            local_12c = DAT_004dbe4c;
            local_130 = (byte *)0x2e9;
            FUN_0043d574(1,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_004dbe50,DAT_004dbe50,uVar2);
          }
          local_120 = *(uint *)(pbVar10 + 0x28);
          local_124 = *(byte **)(pbVar10 + 0x24);
          local_128 = *(uint *)(pbVar10 + 0x20);
          local_12c = *(uint *)(pbVar10 + 0x1c);
          local_130 = *(byte **)(pbVar10 + 0x18);
          FUN_004da4a4(bVar1,5,*(undefined4 *)(pbVar10 + 4),pbVar10 + 8);
          iVar5 = -1;
        }
      }
      else if (bVar8 == 5) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004dbc84;
          local_130 = (byte *)0x29b;
          FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004dbc88,DAT_004dbc88);
        }
        iVar5 = FUN_0045a568();
        if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 1)) {
          uVar7 = FUN_00464bb2(0xe0,param_1,param_2 & 0xffff,0);
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_12c = DAT_004dbc74;
            local_130 = (byte *)0x29e;
            local_128 = uVar7;
            FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if (-1 < iVar5 << 0x1f) {
            iVar5 = FUN_0043d0ce();
            if (-1 < iVar5 << 0x1d) {
              return iVar5 << 0x1d;
            }
          }
          iVar5 = compress_log_output(0x10400000,DAT_004dbc78,DAT_004dbc78,uVar7);
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_12c = DAT_004dbc7c;
            local_130 = (byte *)0x2a0;
            FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004dbc80,DAT_004dbc80);
          }
          iVar5 = FUN_004d9c86(6,bVar1,10,9);
        }
      }
      else if (bVar8 == 7) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004db85c;
          local_130 = (byte *)0x25e;
          FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004db860,DAT_004db860);
        }
        if (uVar2 == 7) {
          puVar9 = (uint *)(pbVar10 + 4);
          if (*puVar9 < 0xd) {
            if ((uint)*(ushort *)(pbVar10 + 0x155c) + (uint)*(ushort *)(pbVar10 + 8) +
                (uint)*(ushort *)(pbVar10 + 0x36a0) < 0xd) {
              bVar12 = 0;
              for (bVar8 = 0; (ushort)bVar8 < *(ushort *)(pbVar10 + 8); bVar8 = bVar8 + 1) {
                if (puVar9[(uint)bVar8 * 0x155 + 0x154] == 1) {
                  bVar12 = bVar12 + 1;
                }
              }
              for (uVar7 = 0; (uVar7 & 0xff) < (uint)*(ushort *)(pbVar10 + 0x155c);
                  uVar7 = uVar7 + 1) {
                if (puVar9[(uVar7 & 0xff) * 0x10a + 0x564] == 1) {
                  bVar12 = bVar12 + 1;
                }
              }
              if (bVar12 < 2) {
                iVar5 = FUN_0045a568();
                if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 1)) {
                  uVar7 = FUN_00464bb2(0xe0,param_1,param_2 & 0xffff,0);
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    local_12c = DAT_004dbc74;
                    local_130 = (byte *)0x28e;
                    local_128 = uVar7;
                    FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0x10400000,DAT_004dbc78,DAT_004dbc78,uVar7);
                  }
                }
                else {
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    local_12c = DAT_004dbc7c;
                    local_130 = (byte *)0x290;
                    FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0x4000000,DAT_004dbc80,DAT_004dbc80);
                  }
                  FUN_004d9c86(8,bVar1,8,7);
                }
                iVar5 = 0;
              }
              else {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  local_128 = (uint)bVar12;
                  local_12c = DAT_004db844;
                  local_130 = (byte *)0x286;
                  FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x4400000,DAT_004db848,DAT_004db848,bVar12);
                }
                FUN_004d9c86(8,bVar1,8,7);
                iVar5 = -4;
              }
            }
            else {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                local_120 = (uint)*(ushort *)(pbVar10 + 0x36a0);
                local_124 = (byte *)(uint)*(ushort *)(pbVar10 + 0x155c);
                local_128 = (uint)*(ushort *)(pbVar10 + 8);
                local_12c = DAT_004db83c;
                local_130 = (byte *)0x270;
                FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                local_12c = (uint)*(ushort *)(pbVar10 + 0x36a0);
                local_130 = (byte *)(uint)*(ushort *)(pbVar10 + 0x155c);
                compress_log_output(0x4c00000,DAT_004db840,DAT_004db840,*(undefined2 *)(pbVar10 + 8)
                                   );
              }
              FUN_004d9c86(8,bVar1,8,7);
              iVar5 = -4;
            }
          }
          else {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              local_128 = *puVar9;
              local_12c = DAT_004db7b8;
              local_130 = (byte *)0x268;
              FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_004db7bc,DAT_004db7bc,*puVar9);
            }
            FUN_004d9c86(8,bVar1,8,7);
            iVar5 = -4;
          }
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_128 = (uint)uVar2;
            local_12c = DAT_004db864;
            local_130 = (byte *)0x261;
            FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_004db868,DAT_004db868,uVar2);
          }
          iVar5 = -1;
        }
      }
      else if (bVar8 == 9) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004dbdcc;
          local_130 = (byte *)0x2a8;
          FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004dbdd0,DAT_004dbdd0);
        }
        iVar5 = FUN_0045a568();
        if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 1)) {
          uVar7 = FUN_00464bb2(0xe0,param_1,param_2 & 0xffff,0);
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_12c = DAT_004dbdd4;
            local_130 = (byte *)0x2ab;
            local_128 = uVar7;
            FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if (-1 < iVar5 << 0x1f) {
            iVar5 = FUN_0043d0ce();
            if (-1 < iVar5 << 0x1d) {
              return iVar5 << 0x1d;
            }
          }
          iVar5 = compress_log_output(0x10400000,DAT_004dbdd8,DAT_004dbdd8,uVar7);
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_12c = DAT_004dbddc;
            local_130 = (byte *)0x2ad;
            FUN_0043d574(1,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004dbde0,DAT_004dbde0);
          }
          iVar5 = FUN_004d9c86(10,bVar1,0xc,0xb);
        }
      }
      else if (bVar8 == 0xc) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004dbde4;
          local_130 = (byte *)0x2b5;
          FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004dbde8,DAT_004dbde8);
        }
        iVar5 = FUN_0045a568();
        if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 1)) {
          uVar7 = FUN_00464bb2(0xe0,param_1,param_2 & 0xffff,0);
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_12c = DAT_004dbdec;
            local_130 = (byte *)0x2b8;
            local_128 = uVar7;
            FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if (-1 < iVar5 << 0x1f) {
            iVar5 = FUN_0043d0ce();
            if (-1 < iVar5 << 0x1d) {
              return iVar5 << 0x1d;
            }
          }
          iVar5 = compress_log_output(0x10400000,DAT_004dbdf0,DAT_004dbdf0,uVar7);
        }
      }
      else if (bVar8 == 0xf) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004dbdf4;
          local_130 = (byte *)0x2be;
          FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004dbdf8,DAT_004dbdf8);
        }
        iVar5 = FUN_0045a568();
        if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 1)) {
          uVar7 = FUN_00464bb2(0xe0,param_1,param_2 & 0xffff,0);
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_12c = DAT_004dbdfc;
            local_130 = (byte *)0x2c1;
            local_128 = uVar7;
            FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if (-1 < iVar5 << 0x1f) {
            iVar5 = FUN_0043d0ce();
            if (-1 < iVar5 << 0x1d) {
              return iVar5 << 0x1d;
            }
          }
          iVar5 = compress_log_output(0x10400000,DAT_004dbe00,DAT_004dbe00,uVar7);
        }
      }
      else if (bVar8 == 0x12) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004dbe28;
          local_130 = (byte *)0x2d8;
          FUN_0043d574(4,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004dbe38,DAT_004dbe38);
        }
        iVar5 = FUN_0045a568();
        if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xffe), iVar5 == 1)) {
          FUN_0043c0e4(&local_fc,0xdc,0);
          FUN_0043c0e4(&local_fc,0xdc,0);
          local_fc = 1;
          local_fb = (undefined1)*(undefined4 *)(pbVar10 + 4);
          pbVar10 = pbVar10 + 8;
          uVar6 = FUN_0044a43c(pbVar10);
          FUN_0044b5a0(auStack_fa,pbVar10,uVar6);
          sVar4 = FUN_0044a43c(pbVar10);
          uVar7 = FUN_00464bb2(0xffe,&local_fc,sVar4 + 2,0);
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_12c = DAT_004dbe3c;
            local_130 = (byte *)0x2e1;
            local_128 = uVar7;
            FUN_0043d574(4,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
          }
          iVar5 = FUN_0043d0ce();
          if (-1 < iVar5 << 0x1f) {
            iVar5 = FUN_0043d0ce();
            if (-1 < iVar5 << 0x1d) {
              return iVar5 << 0x1d;
            }
          }
          iVar5 = compress_log_output(0x10400000,DAT_004dbe40,DAT_004dbe40,uVar7);
        }
      }
      else if (bVar8 == 0x13) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_12c = DAT_004dbe04;
          local_130 = (byte *)0x2c7;
          FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004dbe08,DAT_004dbe08);
        }
        iVar5 = FUN_0045a568();
        if ((iVar5 == 1) && (iVar5 = FUN_004434d0(0xe0), iVar5 == 1)) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            local_124 = *(byte **)(pbVar10 + 8);
            local_128 = *(uint *)(pbVar10 + 4);
            local_12c = DAT_004dbe0c;
            local_130 = (byte *)0x2c9;
            FUN_0043d574(4,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            local_130 = *(byte **)(pbVar10 + 8);
            compress_log_output(0x10800000,DAT_004dbe10,DAT_004dbe10,*(undefined4 *)(pbVar10 + 4));
          }
          FUN_004da720(*(undefined4 *)(pbVar10 + 4),*(undefined4 *)(pbVar10 + 8));
          if (*(int *)(pbVar10 + 4) == 1) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              local_12c = DAT_004dbe14;
              local_130 = (byte *)0x2cc;
              FUN_0043d574(3,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_004dbe18,DAT_004dbe18);
            }
            *DAT_004dbe1c = 1;
          }
          else {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              local_12c = DAT_004dbe20;
              local_130 = (byte *)0x2cf;
              FUN_0043d574(3,DAT_004db4c4,DAT_004db4c0,DAT_004db4bc);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_004dbe24,DAT_004dbe24);
            }
            *DAT_004dbe1c = 0;
          }
          iVar5 = FUN_004da60c(bVar1,*(undefined4 *)(pbVar10 + 4));
        }
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_128 = (uint)bVar8;
          local_12c = DAT_004dbea4;
          local_130 = (byte *)0x37d;
          FUN_0043d574(1,DAT_004dbe34,DAT_004dbe30,DAT_004dbe2c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_004dbea8,DAT_004dbea8,bVar8);
        }
        iVar5 = -1;
      }
    }
  }
  return iVar5;
}

