
/* WARNING: Type propagation algorithm not settling */

int FUN_00481836(code *param_1,int param_2,byte *param_3,int *param_4,undefined1 param_5)

{
  short sVar1;
  code *pcVar2;
  code *pcVar3;
  int iVar4;
  char *pcVar5;
  int iVar6;
  undefined2 *puVar7;
  undefined1 *puVar8;
  int *piVar9;
  undefined4 uVar10;
  byte bVar11;
  undefined *puVar12;
  uint uVar13;
  byte extraout_r2;
  byte *pbVar14;
  uint *puVar15;
  byte bVar16;
  int iVar17;
  uint uVar18;
  short sVar19;
  uint uVar20;
  byte *pbVar21;
  byte *pbVar22;
  uint uVar23;
  char cVar24;
  undefined8 uVar25;
  undefined8 uVar26;
  int local_e8;
  uint local_e4;
  undefined8 local_e0;
  int local_d8;
  byte *local_d4;
  byte *local_d0;
  int local_cc;
  uint local_c8;
  int local_c4;
  int local_c0;
  int local_bc;
  uint local_b8;
  int local_b4;
  uint local_b0;
  int local_ac;
  ushort local_a8;
  byte local_a6;
  undefined1 local_a5;
  byte local_a0 [60];
  byte local_64 [7];
  byte local_5d [33];
  undefined4 local_3c;
  uint local_38;
  uint uStack_34;
  code *local_28;
  
  local_3c = &local_a6;
  local_a5 = param_5;
  local_b4 = 0;
  local_d8 = param_2;
  pcVar2 = param_1;
  do {
    while( true ) {
      local_28 = pcVar2;
      if (*param_3 == 0) {
        return local_b4;
      }
      if (*param_3 == 0x25) break;
      local_d8 = (*local_28)(local_d8,*param_3);
      if (local_d8 == 0) {
        return -1;
      }
      local_b4 = local_b4 + 1;
      param_3 = param_3 + 1;
      pcVar2 = local_28;
    }
    local_a8 = 0;
    local_cc = 0;
    local_c8 = 0;
    local_c4 = 0;
    local_c0 = 0;
    local_bc = 0;
    local_b8 = 0;
    while( true ) {
      while( true ) {
        while( true ) {
          while( true ) {
            while( true ) {
              pbVar21 = param_3 + 1;
              bVar11 = *pbVar21;
              if (bVar11 != 0x20) break;
              local_a8 = local_a8 | 1;
              param_3 = pbVar21;
            }
            if (bVar11 != 0x23) break;
            local_a8 = local_a8 | 8;
            param_3 = pbVar21;
          }
          if (bVar11 != 0x2b) break;
          local_a8 = local_a8 | 2;
          param_3 = pbVar21;
        }
        if (bVar11 != 0x2d) break;
        local_a8 = local_a8 | 4;
        param_3 = pbVar21;
      }
      if (bVar11 != 0x30) break;
      local_a8 = local_a8 | 0x10;
      param_3 = pbVar21;
    }
    if (bVar11 == 0x2a) {
      local_ac = *(int *)*param_4;
      *param_4 = (int)((int *)*param_4 + 1);
      if (local_ac < 0) {
        local_ac = -local_ac;
        local_a8 = local_a8 | 4;
      }
      pbVar21 = param_3 + 2;
    }
    else {
      local_ac = 0;
      for (; *pbVar21 - 0x30 < 10; pbVar21 = pbVar21 + 1) {
        if (local_ac < DAT_004824f0) {
          local_ac = (uint)*pbVar21 + local_ac * 10 + -0x30;
        }
      }
    }
    if (*pbVar21 == 0x2e) {
      bVar11 = pbVar21[1];
      if (bVar11 == 0x2a) {
        local_b0 = *(uint *)*param_4;
        *param_4 = (int)((uint *)*param_4 + 1);
        pbVar21 = pbVar21 + 2;
      }
      else {
        if (bVar11 == 0x2d) {
          cVar24 = '-';
          pbVar21 = pbVar21 + 2;
        }
        else {
          cVar24 = '\0';
          pbVar21 = pbVar21 + 1;
        }
        local_b0 = 0;
        for (; *pbVar21 - 0x30 < 10; pbVar21 = pbVar21 + 1) {
          if ((cVar24 == '\0') && ((int)local_b0 < DAT_004824f0)) {
            local_b0 = ((uint)*pbVar21 + local_b0 * 10) - 0x30;
          }
        }
      }
    }
    else {
      local_b0 = 0xffffffff;
    }
    iVar4 = FUN_00481818(s_hjltzL_004824f4,*pbVar21);
    uVar18 = local_b0;
    local_a6 = 0;
    pbVar22 = pbVar21;
    if (iVar4 != 0) {
      pbVar22 = pbVar21 + 1;
      local_a6 = *pbVar21;
    }
    if (local_a6 == 0x68) {
      if (*pbVar22 == 0x68) {
        local_a6 = 0x62;
LAB_004819ae:
        pbVar22 = pbVar22 + 1;
      }
    }
    else {
      bVar11 = local_a6;
      if (local_a6 == 0x6c) {
        bVar11 = *pbVar22;
      }
      if (local_a6 == 0x6c && bVar11 == 0x6c) {
        local_a6 = 0x71;
        goto LAB_004819ae;
      }
    }
    local_d0 = local_a0;
    param_3 = pbVar22 + 1;
    bVar11 = *pbVar22;
    uVar23 = (uint)bVar11;
    if (uVar23 == 0x25) {
      local_a0[0] = 0x25;
LAB_0048248e:
      local_cc = 1;
      goto LAB_004824ac;
    }
    if ((uVar23 == 0x41) || (uVar23 - 0x45 < 3)) {
LAB_00481cf2:
      if (local_a6 == 0x4c) {
        iVar4 = *param_4;
      }
      else {
        iVar4 = *param_4;
      }
      puVar15 = (uint *)(iVar4 + 7U & 0xfffffff8);
      *param_4 = (int)puVar15;
      local_e0._0_4_ = *puVar15;
      local_e0._4_4_ = puVar15[1];
      *param_4 = (int)(puVar15 + 2);
      if ((int)local_e0._4_4_ < 0) {
        bVar16 = 0x2d;
LAB_00481d3c:
        local_a0[local_cc] = bVar16;
        local_cc = local_cc + 1;
      }
      else {
        if ((int)((uint)local_a8 << 0x1e) < 0) {
          bVar16 = 0x2b;
          goto LAB_00481d3c;
        }
        if ((int)((uint)local_a8 << 0x1f) < 0) {
          bVar16 = 0x20;
          goto LAB_00481d3c;
        }
      }
      local_d4 = local_a0 + local_cc;
      if ((uVar23 | 0x20) != 0x61) {
        if ((int)local_b0 < 0) {
          local_b0 = 6;
        }
        else {
          if (local_b0 == 0) {
            uVar18 = uVar23 | 0x20;
          }
          if (local_b0 == 0 && uVar18 == 0x67) {
            local_b0 = 1;
          }
        }
      }
      uVar18 = local_e0._4_4_ << 1 | (uint)local_e0 >> 0x1f;
      local_38 = (uint)local_e0;
      uStack_34 = local_e0._4_4_;
      if (((int)uVar18 < 0 && (int)uVar18 >> 0x15 == -1) &&
         (((local_e0._4_4_ & 0xfffff) != 0 || (uint)local_e0 >> 0x14 != 0) ||
          ((uint)local_e0 & 0xfffff) != 0)) {
        if (uVar23 - 0x61 < 0x1a) {
          puVar12 = &DAT_004826e8;
        }
        else {
          puVar12 = &DAT_004826ec;
        }
      }
      else {
        if (((int)(local_e0._4_4_ << 1) >> 0x15 != -1) || ((local_e0._4_4_ & 0xfffff) != 0)) {
          local_e0 = FUN_004d4150((uint)local_e0,local_e0._4_4_,&local_e8);
          uVar18 = (uint)(local_e0 >> 0x20);
          iVar4 = (int)local_e0;
          if ((uVar23 | 0x20) == 0x61) {
            *local_d4 = 0x30;
            if (uVar23 == 0x61) {
              bVar16 = 0x78;
            }
            else {
              bVar16 = 0x58;
            }
            local_d4[1] = bVar16;
            local_cc = local_cc + 2;
            local_d4 = local_d4 + 2;
          }
          uVar20 = local_38;
          if ((local_e0 & 0x7fffffff00000000) == 0 && iVar4 == 0) {
            uVar18 = 0;
            pbVar21 = local_64;
            iVar17 = 0;
          }
          else {
            uVar13 = uVar23 | 0x20;
            if (uVar13 == 0x61) {
              if ((int)local_b0 < 0) {
                local_e4 = 0x21;
              }
              else {
                local_e4 = local_b0 + 1;
              }
              cVar24 = 0xfffffffe < local_e4;
              iVar17 = local_e4 + 1;
              FUN_004d41c0(local_38,uStack_34,0,0);
              if (cVar24 == '\0') {
                uVar18 = uVar18 ^ 0x80000000;
              }
              uVar25 = CONCAT44(uVar18,iVar4);
              local_64[0] = extraout_r2;
              local_e8 = local_e8 + -4;
              pbVar21 = local_64 + 1;
              while( true ) {
                if (iVar17 < 1) break;
                cVar24 = '\x01';
                uVar25 = FUN_0043c0b0((int)uVar25,(int)((ulonglong)uVar25 >> 0x20),0,0);
                if (cVar24 != '\0') break;
                uVar25 = FUN_004d41f4((int)uVar25,(int)((ulonglong)uVar25 >> 0x20),0x1c);
                iVar4 = FUN_004d42f8();
                iVar17 = iVar17 + -7;
                if (0 < iVar17) {
                  uVar26 = FUN_004d4306();
                  uVar25 = FUN_004d4314((int)uVar25,(int)((ulonglong)uVar25 >> 0x20),(int)uVar26,
                                        (int)((ulonglong)uVar26 >> 0x20));
                }
                pbVar21 = pbVar21 + 7;
                iVar6 = 7;
                while ((0 < iVar4 && (iVar6 = iVar6 + -1, -1 < iVar6))) {
                  pbVar21 = pbVar21 + -1;
                  *pbVar21 = (byte)iVar4 & 0xf;
                  iVar4 = iVar4 >> 4;
                }
                while (iVar6 = iVar6 + -1, -1 < iVar6) {
                  pbVar21 = pbVar21 + -1;
                  *pbVar21 = 0;
                }
                pbVar21 = pbVar21 + 7;
              }
              uVar20 = (int)pbVar21 - (int)(local_64 + 1);
              pbVar21 = local_64 + 1;
              uVar18 = local_e4;
              if ((int)uVar20 <= (int)local_e4) {
                uVar18 = uVar20;
              }
              if (-1 < (int)uVar18) {
                if (((int)uVar18 < (int)uVar20) && (7 < local_64[uVar18 + 1])) {
                  bVar16 = 0xf;
                }
                else {
                  bVar16 = 0;
                }
                uVar20 = uVar18;
                pbVar22 = local_64 + uVar18;
                while( true ) {
                  if (*pbVar22 != bVar16) break;
                  uVar18 = uVar18 - 1;
                  uVar20 = uVar20 - 1;
                  pbVar22 = pbVar22 + -1;
                }
                if (bVar16 == 0xf) {
                  local_64[uVar20] = local_64[uVar20] + 1;
                }
                if ((int)(uVar20 - 1) < 0) {
                  local_e8 = local_e8 + 4;
                  pbVar21 = local_64;
                  uVar18 = uVar18 + 1;
                }
                iVar4 = uVar18 - 1;
                if (-1 < iVar4) {
                  pbVar22 = pbVar21 + iVar4;
                  do {
                    bVar16 = *pbVar22 + 0x30;
                    if (0x39 < (byte)(*pbVar22 + 0x30)) {
                      bVar16 = (bVar16 + bVar11) - 0x3a;
                    }
                    iVar4 = iVar4 + -1;
                    *pbVar22 = bVar16;
                    pbVar22 = pbVar22 + -1;
                  } while (-1 < iVar4);
                }
              }
              iVar17 = local_e8;
              if ((int)local_b0 < 0) {
                local_b0 = uVar18 - 1;
              }
            }
            else {
              local_e8 = (local_e8 * 0x7597) / DAT_00482674;
              uVar18 = uStack_34 & 0x7fffffff;
              if (7 - local_e8 < 1) {
                uVar25 = FUN_0048262c(0,DAT_00482678,-(7 - local_e8));
                uVar25 = FUN_004d4326(uVar20,uVar18,(int)uVar25,(int)((ulonglong)uVar25 >> 0x20));
              }
              else {
                uVar25 = FUN_0048262c(local_38,uVar18);
              }
              if (uVar13 == 0x66) {
                iVar4 = local_e8 + 10;
              }
              else {
                iVar4 = 6;
              }
              iVar4 = iVar4 + local_b0;
              if (0x14 < iVar4) {
                iVar4 = 0x14;
              }
              local_64[0] = 0x30;
              pbVar21 = local_64 + 1;
              while (0 < iVar4) {
                while( true ) {
                  uVar10 = (undefined4)((ulonglong)uVar25 >> 0x20);
                  uVar20 = FUN_004d4338((int)uVar25,uVar10);
                  iVar17 = 4;
                  uVar18 = uVar20;
                  pbVar22 = pbVar21 + 8;
                  do {
                    pbVar21 = pbVar22;
                    cVar24 = (char)(uVar18 / 10);
                    pbVar21[-1] = (char)uVar18 + cVar24 * -10 + 0x30;
                    uVar18 = (uVar18 / 10) / 10;
                    iVar17 = iVar17 + -1;
                    pbVar21[-2] = cVar24 + (char)uVar18 * -10 + 0x30;
                    pbVar22 = pbVar21 + -2;
                  } while (iVar17 != 0);
                  iVar4 = iVar4 + -8;
                  pbVar21 = pbVar21 + 6;
                  if (iVar4 < 1) break;
                  uVar26 = FUN_004d4346(uVar20);
                  uVar25 = FUN_004d4314((int)uVar25,uVar10,(int)uVar26,
                                        (int)((ulonglong)uVar26 >> 0x20));
                  uVar25 = FUN_004d4354((int)uVar25,(int)((ulonglong)uVar25 >> 0x20),0,DAT_0048267c)
                  ;
                }
              }
              iVar4 = (int)pbVar21 - (int)(local_64 + 1);
              pbVar21 = local_64;
              while (pbVar21 = pbVar21 + 1, *pbVar21 == 0x30) {
                local_e8 = local_e8 + -1;
                iVar4 = iVar4 + -1;
              }
              if (uVar13 == 0x66) {
                iVar17 = local_e8 + 1;
              }
              else if (uVar13 == 0x65) {
                iVar17 = 1;
              }
              else {
                iVar17 = 0;
              }
              uVar18 = iVar17 + local_b0;
              if (iVar4 < (int)uVar18) {
                uVar18 = iVar4 - 1;
              }
              iVar17 = local_e8;
              if (-1 < (int)uVar18) {
                if (((int)uVar18 < iVar4) && (0x34 < pbVar21[uVar18])) {
                  bVar11 = 0x39;
                }
                else {
                  bVar11 = 0x30;
                }
                uVar20 = uVar18;
                pbVar22 = pbVar21 + -1 + uVar18;
                while( true ) {
                  uVar20 = uVar20 - 1;
                  if (*pbVar22 != bVar11) break;
                  uVar18 = uVar18 - 1;
                  pbVar22 = pbVar22 + -1;
                }
                if (bVar11 == 0x39) {
                  pbVar21[uVar20] = pbVar21[uVar20] + 1;
                }
                if ((int)uVar20 < 0) {
                  iVar17 = local_e8 + 1;
                  uVar18 = uVar18 + 1;
                  pbVar21 = pbVar21 + -1;
                  local_e8 = iVar17;
                }
              }
            }
          }
          iVar4 = FUN_004d43a8();
          bVar11 = **(byte **)(iVar4 + 0x24);
          if ((short)uVar18 < 1) {
            uVar18 = 1;
            pbVar21 = &DAT_004826f8;
          }
          sVar1 = (short)uVar18;
          uVar20 = local_b0;
          if ((uVar23 | 0x20) == 0x66) {
LAB_00482112:
            sVar19 = (short)(iVar17 + 1);
            iVar4 = (int)sVar19;
            if (iVar4 < 1) {
              local_d4[local_c8] = 0x30;
              if ((0 < (int)uVar20) ||
                 (uVar23 = local_c8 + 1, (int)((uint)(byte)local_a8 << 0x1c) < 0)) {
                local_d4[local_c8 + 1] = bVar11;
                uVar23 = local_c8 + 2;
              }
              local_c8 = uVar23;
              if ((int)(uVar20 + iVar4) < 0 != SCARRY4(uVar20,iVar4)) {
                sVar19 = -(short)uVar20;
              }
              local_bc = -(int)sVar19;
              uVar20 = (int)sVar19 + uVar20;
              if ((int)uVar20 < (int)sVar1) {
                uVar18 = uVar20;
              }
              iVar4 = (int)(short)uVar18;
              local_c4 = iVar4;
              FUN_00439be4(local_d4 + local_c8,pbVar21,iVar4);
              local_b8 = uVar20 - iVar4;
            }
            else if (sVar1 < sVar19) {
              FUN_00439be4(local_d4 + local_c8,pbVar21,(int)sVar1);
              local_c8 = (int)sVar1 + local_c8;
              local_bc = iVar4 - sVar1;
              local_b8 = uVar20;
              if ((0 < (int)uVar20) || ((int)((uint)(byte)local_a8 << 0x1c) < 0)) {
                local_d4[local_c8] = bVar11;
                local_c4 = local_c4 + 1;
              }
            }
            else {
              FUN_00439be4(local_d4 + local_c8,pbVar21,(int)sVar19);
              uVar18 = uVar18 - (iVar17 + 1);
              iVar17 = local_c8 + iVar4;
              if ((0 < (int)uVar20) || (local_c8 = iVar17, (int)((uint)(byte)local_a8 << 0x1c) < 0))
              {
                local_c8 = iVar17 + 1;
                local_d4[iVar17] = bVar11;
              }
              if ((int)uVar20 < (int)(short)uVar18) {
                uVar18 = uVar20;
              }
              sVar1 = (short)uVar18;
              FUN_00439be4(local_d4 + local_c8,pbVar21 + iVar4,(int)sVar1);
              local_c8 = (int)sVar1 + local_c8;
              local_bc = uVar20 - (int)sVar1;
            }
          }
          else {
            sVar19 = (short)iVar17;
            if ((uVar23 | 0x20) == 0x67) {
              if ((-5 < sVar19) && ((int)sVar19 < (int)local_b0)) {
                if ((-1 < (int)((uint)(byte)local_a8 << 0x1c)) && ((int)sVar1 <= (int)local_b0)) {
                  uVar20 = (int)sVar1;
                }
                uVar20 = uVar20 - (int)(short)(sVar19 + 1);
                if ((int)uVar20 < 0) {
                  uVar20 = 0;
                }
                goto LAB_00482112;
              }
              if (((int)sVar1 < (int)local_b0) && (-1 < (int)((uint)(byte)local_a8 << 0x1c))) {
                uVar20 = (int)sVar1;
              }
              uVar20 = uVar20 - 1;
              if ((int)uVar20 < 0) {
                uVar20 = 0;
              }
              if (uVar23 == 0x67) {
                uVar23 = 0x65;
              }
              else {
                uVar23 = 0x45;
              }
            }
            else if (uVar23 == 0x61) {
              uVar23 = 0x70;
            }
            else if (uVar23 == 0x41) {
              uVar23 = 0x50;
            }
            uVar13 = local_c8 + 1;
            local_d4[local_c8] = *pbVar21;
            if ((0 < (int)uVar20) || ((int)((uint)(byte)local_a8 << 0x1c) < 0)) {
              local_c8 = local_c8 + 2;
              local_d4[uVar13] = bVar11;
              uVar13 = local_c8;
              if (0 < (int)uVar20) {
                uVar13 = uVar18 - 1;
                if ((int)uVar20 < (int)(short)(uVar18 - 1)) {
                  uVar13 = uVar20;
                }
                sVar1 = (short)uVar13;
                FUN_00439be4(local_d4 + local_c8,pbVar21 + 1,(int)sVar1);
                local_bc = uVar20 - (int)sVar1;
                uVar13 = (int)sVar1 + local_c8;
              }
            }
            local_c8 = uVar13;
            pbVar21 = local_d4 + local_c8;
            *pbVar21 = (byte)uVar23;
            if (sVar19 < 0) {
              pbVar21[1] = 0x2d;
              iVar17 = -(int)sVar19;
            }
            else {
              pbVar21[1] = 0x2b;
            }
            pbVar22 = pbVar21 + 2;
            iVar4 = 0;
            puVar15 = &local_38;
            while (0 < (short)iVar17) {
              iVar6 = (int)(short)iVar17 / 10;
              *(char *)puVar15 = (char)iVar17 + (char)iVar6 * -10;
              iVar4 = iVar4 + 1;
              iVar17 = iVar6;
              puVar15 = (uint *)((int)puVar15 + 1);
            }
            pbVar14 = pbVar22;
            if ((iVar4 < 2) && ((uVar23 | 0x20) == 0x65)) {
              pbVar14 = pbVar21 + 3;
              *pbVar22 = 0x30;
            }
            pbVar21 = pbVar14;
            if (iVar4 == 0) {
              pbVar21 = pbVar14 + 1;
              *pbVar14 = 0x30;
            }
            else {
              for (; 0 < iVar4; iVar4 = iVar4 + -1) {
                *pbVar21 = *(char *)((int)&local_3c + iVar4 + 3) + 0x30;
                pbVar21 = pbVar21 + 1;
              }
            }
            local_c4 = (int)pbVar21 - (int)(local_d4 + local_c8);
          }
          if ((((byte)local_a8 & 0x14) == 0x10) &&
             (iVar4 = local_b8 + local_c4 + local_bc + local_c8 + local_cc, iVar4 < local_ac)) {
            local_c0 = local_ac - iVar4;
          }
          goto LAB_004824ac;
        }
        if (uVar23 - 0x61 < 0x1a) {
          puVar12 = &DAT_004826f0;
        }
        else {
          puVar12 = &DAT_004826f4;
        }
      }
      local_c8 = 3;
      FUN_00439be4(local_d4,puVar12,3);
    }
    else {
      if (uVar23 == 0x58) goto LAB_00482348;
      if (uVar23 == 0x61) goto LAB_00481cf2;
      if (uVar23 == 99) {
        local_a0[0] = (byte)*(undefined4 *)*param_4;
        *param_4 = (int)((undefined4 *)*param_4 + 1);
        goto LAB_0048248e;
      }
      if (uVar23 == 100) {
LAB_004823de:
        if (local_a6 == 0x62) {
          uVar10 = *(undefined4 *)*param_4;
          *param_4 = (int)((undefined4 *)*param_4 + 1);
          local_e0._0_4_ = (uint)(char)uVar10;
LAB_0048243e:
          local_e0._4_4_ = (int)(uint)local_e0 >> 0x1f;
        }
        else {
          if (local_a6 == 0x68) {
            uVar10 = *(undefined4 *)*param_4;
            *param_4 = (int)((undefined4 *)*param_4 + 1);
            local_e0._0_4_ = (uint)(short)uVar10;
            goto LAB_0048243e;
          }
          if ((local_a6 != 0x6a) && ((local_a6 == 0x6c || (local_a6 != 0x71)))) {
            local_e0._0_4_ = *(uint *)*param_4;
            *param_4 = (int)((uint *)*param_4 + 1);
            goto LAB_0048243e;
          }
          puVar15 = (uint *)(*param_4 + 7U & 0xfffffff8);
          *param_4 = (int)puVar15;
          local_e0._0_4_ = *puVar15;
          local_e0._4_4_ = puVar15[1];
          *param_4 = (int)(puVar15 + 2);
        }
        if ((int)local_e0._4_4_ < 0) {
          bVar11 = 0x2d;
LAB_00482464:
          local_a0[local_cc] = bVar11;
          local_cc = local_cc + 1;
        }
        else {
          if ((int)((uint)local_a8 << 0x1e) < 0) {
            bVar11 = 0x2b;
            goto LAB_00482464;
          }
          if ((int)((uint)local_a8 << 0x1f) < 0) {
            bVar11 = 0x20;
            goto LAB_00482464;
          }
        }
LAB_0048246c:
        local_d4 = local_a0 + local_cc;
LAB_00482476:
        FUN_00482518(&local_e0,uVar23);
      }
      else {
        if (uVar23 - 0x65 < 3) goto LAB_00481cf2;
        if (uVar23 == 0x69) goto LAB_004823de;
        if (uVar23 != 0x6e) {
          if (uVar23 == 0x6f) {
LAB_00482348:
            if (local_a6 == 0x62) {
              uVar18 = *(uint *)*param_4;
              *param_4 = (int)((uint *)*param_4 + 1);
              local_e0._0_4_ = uVar18 & 0xff;
LAB_004823a8:
              local_e0._4_4_ = 0;
            }
            else {
              if (local_a6 == 0x68) {
                uVar18 = *(uint *)*param_4;
                *param_4 = (int)((uint *)*param_4 + 1);
                local_e0._0_4_ = uVar18 & 0xffff;
                goto LAB_004823a8;
              }
              if ((local_a6 != 0x6a) && ((local_a6 == 0x6c || (local_a6 != 0x71)))) {
                local_e0._0_4_ = *(uint *)*param_4;
                *param_4 = (int)((uint *)*param_4 + 1);
                goto LAB_004823a8;
              }
              puVar15 = (uint *)(*param_4 + 7U & 0xfffffff8);
              *param_4 = (int)puVar15;
              local_e0._0_4_ = *puVar15;
              local_e0._4_4_ = puVar15[1];
              *param_4 = (int)(puVar15 + 2);
            }
            if ((((int)((uint)(byte)local_a8 << 0x1c) < 0) &&
                (local_e0._4_4_ != 0 || (uint)local_e0 != 0)) && ((uVar23 | 0x20) == 0x78)) {
              local_a0[local_cc] = 0x30;
              local_a0[local_cc + 1] = bVar11;
              local_cc = local_cc + 2;
            }
            goto LAB_0048246c;
          }
          if (uVar23 != 0x70) {
            if (uVar23 == 0x73) {
              pbVar21 = *(byte **)*param_4;
              *param_4 = (int)((undefined4 *)*param_4 + 1);
              local_d4 = pbVar21;
              if (pbVar21 == (byte *)0x0) {
                if (local_3c[1] != 0) {
                  pcVar5 = s_printf_s__bad__s_argument_004824fc;
                  goto LAB_00481a4e;
                }
                local_d4 = &DAT_004826e4;
              }
              else if ((int)local_b0 < 0) {
                local_c8 = FUN_0044a43c(pbVar21);
              }
              else {
                iVar4 = FUN_004d40e0(pbVar21,0,local_b0);
                local_c8 = uVar18;
                if (iVar4 != 0) {
                  local_c8 = iVar4 - (int)pbVar21;
                }
              }
            }
            else {
              if ((uVar23 == 0x75) || (uVar23 == 0x78)) goto LAB_00482348;
              local_cc = 1;
              local_a0[0] = 0x25;
              if (uVar23 != 0) {
                local_cc = 2;
                local_a0[1] = bVar11;
              }
            }
            goto LAB_004824ac;
          }
          local_e0._0_4_ = *(uint *)*param_4;
          *param_4 = (int)((uint *)*param_4 + 1);
          local_e0._4_4_ = 0;
          local_d4 = local_a0;
          uVar23 = 0x78;
          goto LAB_00482476;
        }
        if (local_3c[1] == 0) {
          if (local_a6 != 0x62) {
            if (local_a6 == 0x68) {
              puVar7 = *(undefined2 **)*param_4;
              *param_4 = (int)((undefined4 *)*param_4 + 1);
              if (puVar7 != (undefined2 *)0x0) {
                *puVar7 = (short)local_b4;
                goto LAB_004824ac;
              }
              pcVar5 = s_printf__bad__n_argument_004826cc;
            }
            else if (local_a6 == 0x6a) {
              piVar9 = *(int **)*param_4;
              *param_4 = (int)((int *)*param_4 + 1);
              if (piVar9 != (int *)0x0) {
LAB_00481cac:
                *piVar9 = local_b4;
                piVar9[1] = local_b4 >> 0x1f;
                goto LAB_004824ac;
              }
              pcVar5 = s_printf__bad__n_argument_004826cc;
            }
            else if (local_a6 == 0x6c) {
              piVar9 = *(int **)*param_4;
              *param_4 = (int)((int *)*param_4 + 1);
              if (piVar9 != (int *)0x0) goto LAB_00481cec;
              pcVar5 = s_printf__bad__n_argument_004826cc;
            }
            else if (local_a6 == 0x71) {
              piVar9 = *(int **)*param_4;
              *param_4 = (int)((int *)*param_4 + 1);
              if (piVar9 != (int *)0x0) goto LAB_00481cac;
              pcVar5 = s_printf__bad__n_argument_004826cc;
            }
            else if (local_a6 == 0x74) {
              piVar9 = *(int **)*param_4;
              *param_4 = (int)((int *)*param_4 + 1);
              if (piVar9 != (int *)0x0) goto LAB_00481cec;
              pcVar5 = s_printf__bad__n_argument_004826cc;
            }
            else if (local_a6 == 0x7a) {
              piVar9 = *(int **)*param_4;
              *param_4 = (int)((int *)*param_4 + 1);
              if (piVar9 != (int *)0x0) goto LAB_00481cec;
              pcVar5 = s_printf__bad__n_argument_004826cc;
            }
            else {
              piVar9 = *(int **)*param_4;
              *param_4 = (int)((int *)*param_4 + 1);
              if (piVar9 != (int *)0x0) {
LAB_00481cec:
                *piVar9 = local_b4;
                goto LAB_004824ac;
              }
              pcVar5 = s_printf__bad__n_argument_004826cc;
            }
            goto LAB_00481a4e;
          }
          puVar8 = *(undefined1 **)*param_4;
          *param_4 = (int)((undefined4 *)*param_4 + 1);
          if (puVar8 == (undefined1 *)0x0) {
            pcVar5 = s_printf__bad__n_argument_004826cc;
            goto LAB_00481a4e;
          }
          *puVar8 = (char)local_b4;
        }
        else {
          pcVar5 = s_printf_s___n_disallowed_004826b4;
LAB_00481a4e:
          iVar4 = FUN_004d40a0(pcVar5);
          if (iVar4 != -1) {
            return -1;
          }
        }
      }
    }
LAB_004824ac:
    pcVar2 = local_28;
    iVar4 = (((((local_ac - local_cc) - local_c0) - local_c8) - local_bc) - local_c4) - local_b8;
    if (-1 < (int)((uint)(byte)local_a8 << 0x1d)) {
      local_e8 = CONCAT31(local_e8._1_3_,0x20);
      iVar17 = iVar4;
      if (0 < iVar4) {
        do {
          iVar6 = FUN_00482684(pcVar2,&local_e0,&local_e8,1);
          if (iVar6 != 0) {
            return -1;
          }
          iVar17 = iVar17 + -1;
        } while (iVar17 != 0);
        local_28 = pcVar2;
      }
    }
    pcVar2 = local_28;
    pbVar21 = local_a0;
    iVar6 = local_c0;
    for (iVar17 = local_cc; local_c0 = iVar6, iVar17 != 0; iVar17 = iVar17 + -1) {
      local_d8 = (*pcVar2)(local_d8,*pbVar21);
      if (local_d8 == 0) {
        return -1;
      }
      local_b4 = local_b4 + 1;
      pbVar21 = pbVar21 + 1;
      iVar6 = local_c0;
    }
    local_e8._1_3_ = (undefined3)((uint)local_e8 >> 8);
    local_e8._0_1_ = 0x30;
    local_28 = pcVar2;
    pbVar21 = local_d4;
    uVar18 = local_c8;
    iVar17 = local_bc;
    pcVar3 = pcVar2;
    if (0 < iVar6) {
      do {
        iVar17 = FUN_00482684(pcVar2,&local_e0,&local_e8,1);
        if (iVar17 != 0) {
          return -1;
        }
        iVar6 = iVar6 + -1;
        pbVar21 = local_d4;
        uVar18 = local_c8;
        iVar17 = local_bc;
      } while (iVar6 != 0);
    }
    for (; local_28 = pcVar3, local_bc = iVar17, uVar18 != 0; uVar18 = uVar18 - 1) {
      local_d8 = (*pcVar2)(local_d8,*pbVar21);
      if (local_d8 == 0) {
        return -1;
      }
      local_b4 = local_b4 + 1;
      pbVar21 = pbVar21 + 1;
      iVar17 = local_bc;
      pcVar3 = local_28;
    }
    local_e8 = CONCAT31(local_e8._1_3_,0x30);
    local_28 = pcVar2;
    if (0 < iVar17) {
      do {
        iVar6 = FUN_00482684(pcVar2,&local_e0,&local_e8,1);
        if (iVar6 != 0) {
          return -1;
        }
        iVar17 = iVar17 + -1;
      } while (iVar17 != 0);
    }
    pbVar21 = local_d4 + local_c8;
    uVar18 = local_b8;
    local_28 = pcVar2;
    for (iVar17 = local_c4; local_b8 = uVar18, iVar17 != 0; iVar17 = iVar17 + -1) {
      local_d8 = (*pcVar2)(local_d8,*pbVar21);
      if (local_d8 == 0) {
        return -1;
      }
      local_b4 = local_b4 + 1;
      pbVar21 = pbVar21 + 1;
      uVar18 = local_b8;
    }
    local_e8._1_3_ = (undefined3)((uint)local_e8 >> 8);
    local_e8 = CONCAT31(local_e8._1_3_,0x30);
    local_28 = pcVar2;
    if (0 < (int)uVar18) {
      do {
        iVar17 = FUN_00482684(pcVar2,&local_e0,&local_e8,1);
        if (iVar17 != 0) {
          return -1;
        }
        uVar18 = uVar18 - 1;
      } while (uVar18 != 0);
    }
    if ((int)((uint)(byte)local_a8 << 0x1d) < 0) {
      local_e8 = CONCAT31(local_e8._1_3_,0x20);
      local_28 = pcVar2;
      if (0 < iVar4) {
        do {
          iVar17 = FUN_00482684(pcVar2,&local_e0,&local_e8,1);
          if (iVar17 != 0) {
            return -1;
          }
          iVar4 = iVar4 + -1;
        } while (iVar4 != 0);
      }
    }
  } while( true );
}

