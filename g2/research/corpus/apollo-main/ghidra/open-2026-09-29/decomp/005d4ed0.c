
/* WARNING: Type propagation algorithm not settling */

void FUN_005d4ed0(undefined4 *param_1,undefined4 param_2,undefined4 param_3,int param_4,char param_5
                 ,uint param_6,uint param_7,int *param_8)

{
  char cVar1;
  byte bVar2;
  short sVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  int iVar9;
  uint *puVar10;
  int iVar11;
  uint uVar12;
  undefined4 uVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  undefined1 uVar17;
  undefined1 *puVar18;
  int iVar19;
  undefined4 uVar20;
  int iVar21;
  int *piVar22;
  uint uVar23;
  uint uVar24;
  uint uVar25;
  uint uVar26;
  bool bVar27;
  int local_3ed4;
  bool local_3ed0;
  char local_3ecf;
  char local_3ece;
  int *local_3ecc;
  int local_3ec8;
  uint local_3ec4;
  uint local_3ec0;
  uint local_3ebc;
  uint local_3eb8;
  int local_3eb4;
  int local_3eb0;
  uint local_3eac;
  undefined4 local_3ea8;
  undefined1 auStack_3ea4 [16];
  undefined1 auStack_3e94 [4];
  undefined1 local_3e90;
  undefined1 local_3e8f;
  undefined1 auStack_3e78 [32];
  undefined1 auStack_3e58 [32];
  undefined1 auStack_3e38 [8];
  uint auStack_3e30 [15];
  undefined1 auStack_3df4 [28];
  undefined1 auStack_3dd8 [3868];
  undefined1 auStack_2ebc [7744];
  undefined1 auStack_107c [3868];
  undefined1 auStack_160 [172];
  undefined4 auStack_b4 [33];
  undefined4 *local_30;
  undefined4 local_2c;
  int local_28;
  
  iVar19 = 0;
  iVar21 = param_1[0x2c];
  local_3ecc = param_1 + 1;
  uVar20 = *param_1;
  local_3ea8 = param_1[0xd];
  local_30 = param_1;
  local_2c = param_3;
  local_28 = param_4;
  local_3eb4 = FUN_005d3500(iVar21);
  local_3ece = '\0';
  local_3ecf = '\0';
  local_3ec8 = 0;
  local_3ec4 = param_7;
  local_3eb0 = DAT_005d5b88;
  FUN_0043c0e4(auStack_b4,0x80,0);
  FUN_0043c0e4(auStack_3e30 + 0xc,0xc,0);
  FUN_0043c0e4(auStack_3e30 + 6,0x18,0);
  FUN_005d22f2(auStack_3e38,uVar20,local_3ecc,0x10);
  FUN_005d22f2(auStack_3e58,uVar20,local_3ecc,0x14);
  FUN_005d22f2(auStack_3e78,uVar20,local_3ecc,0x14);
  FUN_005d4afe(auStack_3e94,local_3ecc);
  local_3ed4 = local_28;
  FUN_005d3ed0(auStack_2ebc,local_30,local_2c,local_3ea8,auStack_3e58,auStack_3e78,auStack_3e94,
               local_3ec4,local_30 + 0x3c);
  local_3ed0 = *(char *)((int)local_30 + 9) != '\0';
  iVar5 = FUN_005d34f4(iVar21);
  *param_8 = iVar5;
  if (*(char *)((int)local_30 + 9) == '\0') {
    local_3eac = 0x30;
  }
  else {
    local_3eac = FUN_005d3248(iVar21);
  }
  iVar5 = FUN_005d6dca(uVar20,local_3ecc,local_3eac);
  if (iVar5 == 0) {
    iVar19 = 0x40;
  }
  else {
    FUN_005d2390(auStack_3e38,0x11);
    iVar6 = FUN_005d23b6(auStack_3e38);
    FUN_00439c04(iVar6,param_2,0x10);
    local_3ed4 = 0;
    iVar7 = iVar19;
    uVar12 = 0;
    if (*local_3ecc == 0) {
LAB_005d509c:
      while( true ) {
        iVar19 = FUN_005d6db8(iVar6);
        if (iVar19 == 0) {
          bVar2 = FUN_005d6d98(iVar6);
          if (((bVar2 == 0xb) || (bVar2 == 0xe)) && (*(char *)((int)local_30 + 9) != '\0')) {
            bVar2 = 0;
          }
        }
        else if (local_3ed4 == 0) {
          bVar2 = 0xe;
        }
        else {
          bVar2 = 0xb;
        }
        if (*(char *)(local_30 + 2) == '\0') break;
        if ((((local_3ecf != '\0') || (bVar2 == 1)) ||
            ((bVar2 == 3 || ((bVar2 == 0xd || (bVar2 == 10)))))) ||
           ((bVar2 == 0xb || (((bVar2 == 0xc || (bVar2 == 0xe)) || (0x1f < bVar2)))))) {
          if (((0 < local_3ec8) && (bVar2 != 10)) &&
             ((bVar2 != 0xb && ((bVar2 != 0xc && (bVar2 < 0x20)))))) {
            local_3ec8 = 0;
          }
          if (((local_3ece != '\0') && (bVar2 < 0x20)) && (bVar2 != 0xc)) {
            local_3ece = '\0';
          }
          break;
        }
        FUN_005d709c(iVar5);
      }
      iVar19 = iVar7;
      if (*local_3ecc != 0) goto LAB_005d5034;
      local_3eb0 = local_3eb0 + -1;
      if (local_3eb0 == 0) {
        iVar19 = 0x12;
        goto LAB_005d5034;
      }
      if ((bVar2 != 0) && (bVar2 != 2)) {
        if (bVar2 < 2) {
LAB_005d5368:
          if ((*(char *)(local_30 + 2) != '\0') ||
             (iVar14 = FUN_005d4b14(auStack_3e94), iVar14 == 0)) {
            if (*(char *)(local_30 + 2) == '\0') {
              uVar20 = 0;
            }
            else {
              uVar20 = *(undefined4 *)(*(int *)(iVar21 + 0x20) + 4);
            }
            FUN_005d4bba(local_30,iVar5,auStack_3e58,param_8,&local_3ed0,uVar20);
            cVar1 = *(char *)(iVar21 + 0x224);
joined_r0x005d59e8:
            if (cVar1 != '\0') goto LAB_005d5034;
          }
        }
        else if (bVar2 == 4) {
          uVar16 = FUN_005d6e44(iVar5);
          if ((1 < uVar16) && (local_3ed0 == false)) {
            iVar14 = FUN_005d6f38(iVar5,0);
            *param_8 = local_3eb4 + iVar14;
          }
          local_3ed0 = true;
          if (*(char *)(iVar21 + 0x224) != '\0') goto LAB_005d5034;
          iVar19 = FUN_005d6ee0(iVar5);
          param_7 = iVar19 + param_7;
          if (*(int *)(iVar21 + 0x1d4) == 0) {
            FUN_005d4754(auStack_2ebc,param_6,param_7);
          }
        }
        else {
          if (3 < bVar2) {
            if (bVar2 != 6) {
              if (bVar2 < 6) {
                uVar16 = FUN_005d6e44(iVar5);
                for (uVar23 = 0; uVar23 < uVar16; uVar23 = uVar23 + 2) {
                  iVar19 = FUN_005d6f38(iVar5,uVar23);
                  param_6 = iVar19 + param_6;
                  iVar19 = FUN_005d6f38(iVar5,uVar23 + 1);
                  param_7 = iVar19 + param_7;
                  FUN_005d47d4(auStack_2ebc,param_6,param_7);
                }
                FUN_005d709c(iVar5);
                goto LAB_005d509c;
              }
              if (bVar2 == 8) {
LAB_005d55a6:
                local_3eb8 = FUN_005d6e44(iVar5);
                for (iVar19 = 0; iVar19 + 6U <= local_3eb8; iVar19 = iVar19 + 6) {
                  iVar14 = FUN_005d6f38(iVar5,iVar19);
                  local_3ebc = param_6 + iVar14;
                  iVar14 = FUN_005d6f38(iVar5,iVar19 + 1);
                  local_3ec0 = param_7 + iVar14;
                  iVar14 = FUN_005d6f38(iVar5,iVar19 + 2);
                  local_3ec4 = local_3ebc + iVar14;
                  iVar14 = FUN_005d6f38(iVar5,iVar19 + 3);
                  iVar14 = local_3ec0 + iVar14;
                  iVar15 = FUN_005d6f38(iVar5,iVar19 + 4);
                  uVar16 = local_3ec4 + iVar15;
                  iVar15 = FUN_005d6f38(iVar5,iVar19 + 5);
                  FUN_005d4912(auStack_2ebc,local_3ebc,local_3ec0,local_3ec4,iVar14,uVar16,
                               iVar14 + iVar15);
                  param_6 = uVar16;
                  param_7 = iVar14 + iVar15;
                }
                if (bVar2 == 0x18) {
                  iVar14 = FUN_005d6f38(iVar5,iVar19);
                  param_6 = iVar14 + param_6;
                  iVar19 = FUN_005d6f38(iVar5,iVar19 + 1);
                  param_7 = iVar19 + param_7;
                  FUN_005d47d4(auStack_2ebc,param_6,param_7);
                }
                FUN_005d709c(iVar5);
                goto LAB_005d509c;
              }
              if (7 < bVar2) {
                if (bVar2 == 10) {
LAB_005d56da:
                  if (((*(char *)(local_30 + 2) == '\0') && (0x10 < local_3ed4)) ||
                     ((*(char *)(local_30 + 2) != '\0' && (0x10 < local_3ed4)))) {
                    iVar19 = 0x12;
                    goto LAB_005d5034;
                  }
                  iVar6 = FUN_005d23ba(auStack_3e38,local_3ed4 + 1);
                  uVar20 = FUN_005d6ea8(iVar5);
                  if ((*(char *)(local_30 + 2) != '\0') && (*(int *)(iVar21 + 0x264) != 0)) {
                    puVar8 = (undefined4 *)
                             ft_hash_num_lookup(uVar20,*(undefined4 *)(iVar21 + 0x264));
                    if (puVar8 == (undefined4 *)0x0) {
                      uVar20 = 0xffffffff;
                    }
                    else {
                      uVar20 = *puVar8;
                    }
                  }
                  if (bVar2 == 0x1d) {
                    iVar19 = FUN_005d331e(iVar21,uVar20,iVar6);
                    if (iVar19 != 0) {
                      iVar19 = 0x12;
                      goto LAB_005d5034;
                    }
                  }
                  else {
                    iVar19 = FUN_005d3466(iVar21,uVar20,iVar6);
                    if (iVar19 != 0) {
                      iVar19 = 0x12;
                      goto LAB_005d5034;
                    }
                  }
                  local_3ed4 = local_3ed4 + 1;
                  goto LAB_005d509c;
                }
                if (bVar2 < 10) {
                  if (*(char *)(local_30 + 2) != '\0') {
                    FUN_005d1986(iVar21);
                    local_3ed0 = true;
                  }
                }
                else if (bVar2 == 0xc) {
                  bVar2 = FUN_005d6d98(iVar6);
                  if (((((bVar2 != 8) && (bVar2 != 0xd)) && (bVar2 != 0x13)) &&
                      ((bVar2 != 0x19 && (bVar2 != 0x1f)))) && (bVar2 != 0x20)) {
                    if (bVar2 == 0x22) {
                      FUN_005d4c88(iVar5,&param_6,&param_7,auStack_2ebc,DAT_005d5b8c,0);
                      goto LAB_005d509c;
                    }
                    if (bVar2 == 0x23) {
                      FUN_005d4c88(iVar5,&param_6,&param_7,auStack_2ebc,DAT_005d5b90,0);
                    }
                    else {
                      if (bVar2 == 0x24) {
                        FUN_005d4c88(iVar5,&param_6,&param_7,auStack_2ebc,DAT_005d5b94,0);
                        goto LAB_005d509c;
                      }
                      if (bVar2 == 0x25) {
                        FUN_005d4c88(iVar5,&param_6,&param_7,auStack_2ebc,DAT_005d5b98,1);
                        goto LAB_005d509c;
                      }
                      if ((*(char *)((int)local_30 + 9) == '\0') && (bVar2 < 0x26)) {
                        if ((*(char *)(local_30 + 2) == '\0') ||
                           ((local_3ec8 < 1 || (bVar2 == 0x11)))) {
                          if (bVar2 != 0) {
                            if ((bVar2 == 1) || (bVar2 == 2)) {
                              if (*(char *)(local_30 + 2) != '\0') {
                                iVar14 = FUN_005d6f38(iVar5,0);
                                iVar15 = FUN_005d6f38(iVar5,2);
                                iVar9 = FUN_005d6f38(iVar5,4);
                                iVar11 = FUN_005d6f38(iVar5,1);
                                FUN_005d6f9e(iVar5,2,(iVar15 - iVar14) - iVar11);
                                iVar14 = FUN_005d6f38(iVar5,3);
                                FUN_005d6f9e(iVar5,4,(iVar9 - iVar15) - iVar14);
                                if (bVar2 == 1) {
                                  uVar20 = **(undefined4 **)(iVar21 + 0x20);
                                  puVar18 = auStack_3e78;
                                }
                                else {
                                  uVar20 = *(undefined4 *)(*(int *)(iVar21 + 0x20) + 4);
                                  puVar18 = auStack_3e58;
                                }
                                FUN_005d4bba(local_30,iVar5,puVar18,param_8,&local_3ed0,uVar20);
                                cVar1 = *(char *)(iVar21 + 0x224);
                                goto joined_r0x005d59e8;
                              }
                            }
                            else {
                              if (bVar2 == 3) {
                                iVar19 = FUN_005d6ee0(iVar5);
                                iVar14 = FUN_005d6ee0(iVar5);
                                if ((iVar14 == 0) || (iVar19 == 0)) {
                                  uVar17 = 0;
                                }
                                else {
                                  uVar17 = 1;
                                }
                                FUN_005d6e50(iVar5,uVar17);
                                goto LAB_005d509c;
                              }
                              if (bVar2 == 4) {
                                iVar19 = FUN_005d6ee0(iVar5);
                                iVar14 = FUN_005d6ee0(iVar5);
                                FUN_005d6e50(iVar5,iVar14 != 0 || iVar19 != 0);
                                goto LAB_005d509c;
                              }
                              if (bVar2 == 5) {
                                iVar19 = FUN_005d6ee0(iVar5);
                                FUN_005d6e50(iVar5,iVar19 == 0);
                                goto LAB_005d509c;
                              }
                              if (bVar2 == 6) {
                                if (*(char *)(local_30 + 2) != '\0') {
                                  iVar19 = *(int *)(iVar21 + 4);
                                  iVar6 = FUN_005d6ea8(iVar5);
                                  iVar14 = FUN_005d6ea8(iVar5);
                                  local_3ed4 = FUN_005d6ee0(iVar5);
                                  iVar15 = FUN_005d6ee0(iVar5);
                                  iVar9 = FUN_005d6ee0(iVar5);
                                  if (param_5 == '\0') {
                                    if (*(char *)(iVar21 + 0x2f) == '\0') {
                                      if ((*(int *)(iVar21 + 0x244) == 0) &&
                                         (*(int *)(*(int *)(iVar19 + 0x80) + 0x34) == 0)) {
                                        iVar19 = 0x12;
                                      }
                                      else {
                                        iVar15 = **(int **)(iVar21 + 0x20) + iVar15;
                                        if (*(int *)(*(int *)(iVar19 + 0x80) + 0x34) == 0) {
                                          iVar14 = FUN_005d1ed0(iVar21,iVar14);
                                          iVar6 = FUN_005d1ed0(iVar21,iVar6);
                                        }
                                        if ((iVar14 < 0) || (iVar6 < 0)) {
                                          iVar19 = 0x12;
                                        }
                                        else if (*(char *)(iVar21 + 0x2e) == '\0') {
                                          FT_GlyphLoader_Prepare(*(undefined4 *)(iVar21 + 0xc));
                                          iVar19 = FUN_005d33d4(iVar21,iVar14,auStack_3ea4);
                                          if (iVar19 == 0) {
                                            FUN_005d4ed0(local_30,auStack_3ea4,local_2c,local_28,1,0
                                                         ,0,&local_3ec8);
                                            FUN_005d3434(iVar21,auStack_3ea4);
                                            uVar20 = **(undefined4 **)(iVar21 + 0x20);
                                            uVar13 = (*(undefined4 **)(iVar21 + 0x20))[1];
                                            local_3ec4 = **(uint **)(iVar21 + 0x24);
                                            local_3ec0 = (*(uint **)(iVar21 + 0x24))[1];
                                            **(undefined4 **)(iVar21 + 0x20) = 0;
                                            *(undefined4 *)(*(int *)(iVar21 + 0x20) + 4) = 0;
                                            iVar19 = FUN_005d33d4(iVar21,iVar6,auStack_3ea4);
                                            if (iVar19 == 0) {
                                              FUN_005d4ed0(local_30,auStack_3ea4,local_2c,local_28,1
                                                           ,iVar15 - iVar9,local_3ed4,&local_3ec8);
                                              FUN_005d3434(iVar21,auStack_3ea4);
                                              puVar8 = *(undefined4 **)(iVar21 + 0x20);
                                              *puVar8 = uVar20;
                                              puVar8[1] = uVar13;
                                              puVar10 = *(uint **)(iVar21 + 0x24);
                                              *puVar10 = local_3ec4;
                                              puVar10[1] = local_3ec0;
                                              iVar19 = iVar7;
                                            }
                                          }
                                        }
                                        else {
                                          iVar21 = *(int *)(iVar21 + 8);
                                          iVar11 = **(int **)(iVar21 + 0x9c);
                                          iVar19 = FT_GlyphLoader_CheckSubGlyphs(iVar11,2);
                                          if (iVar19 == 0) {
                                            piVar22 = *(int **)(iVar11 + 0x58);
                                            *piVar22 = iVar14;
                                            *(undefined2 *)(piVar22 + 1) = 0x202;
                                            piVar22[2] = 0;
                                            piVar22[3] = 0;
                                            piVar22[8] = iVar6;
                                            *(undefined2 *)(piVar22 + 9) = 2;
                                            iVar19 = FT_RoundFix(iVar15 - iVar9);
                                            piVar22[10] = iVar19 >> 0x10;
                                            iVar19 = FT_RoundFix(local_3ed4);
                                            piVar22[0xb] = iVar19 >> 0x10;
                                            *(undefined4 *)(iVar21 + 0x80) = 2;
                                            *(undefined4 *)(iVar21 + 0x84) =
                                                 *(undefined4 *)(iVar11 + 0x34);
                                            *(undefined4 *)(iVar21 + 0x48) = DAT_005d5b9c;
                                            *(undefined4 *)(iVar11 + 0x54) = 2;
                                            iVar19 = iVar7;
                                          }
                                        }
                                      }
                                    }
                                    else {
                                      iVar19 = 0x12;
                                    }
                                  }
                                  else {
                                    iVar19 = 0x12;
                                  }
                                  goto LAB_005d5034;
                                }
                              }
                              else if (bVar2 == 7) {
                                if (*(char *)(local_30 + 2) != '\0') {
                                  uVar20 = FUN_005d6ee0(iVar5);
                                  *(undefined4 *)(*(int *)(iVar21 + 0x24) + 4) = uVar20;
                                  uVar20 = FUN_005d6ee0(iVar5);
                                  **(undefined4 **)(iVar21 + 0x24) = uVar20;
                                  iVar14 = FUN_005d6ee0(iVar5);
                                  iVar15 = FUN_005d6ee0(iVar5);
                                  **(int **)(iVar21 + 0x20) = iVar15 + **(int **)(iVar21 + 0x20);
                                  *(int *)(*(int *)(iVar21 + 0x20) + 4) =
                                       iVar14 + *(int *)(*(int *)(iVar21 + 0x20) + 4);
                                  local_3ed0 = true;
                                  if (*(char *)(iVar21 + 0x2f) != '\0') goto LAB_005d5034;
                                  if (local_3ecf != '\0') {
                                    param_6 = iVar15 + param_6;
                                    param_7 = iVar14 + param_7;
                                  }
                                }
                              }
                              else {
                                if (bVar2 == 9) {
                                  iVar19 = FUN_005d6ee0(iVar5);
                                  if (iVar19 == -0x80000000) {
                                    FUN_005d6e7c(iVar5,0x7fffffff);
                                  }
                                  else {
                                    if (iVar19 < 0) {
                                      iVar19 = -iVar19;
                                    }
                                    FUN_005d6e7c(iVar5,iVar19);
                                  }
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 10) {
                                  iVar19 = FUN_005d6ee0(iVar5);
                                  iVar14 = FUN_005d6ee0(iVar5);
                                  FUN_005d6e7c(iVar5,iVar19 + iVar14);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0xb) {
                                  iVar19 = FUN_005d6ee0(iVar5);
                                  iVar14 = FUN_005d6ee0(iVar5);
                                  FUN_005d6e7c(iVar5,iVar14 - iVar19);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0xc) {
                                  if ((*(char *)(local_30 + 2) == '\0') || (local_3ece == '\0')) {
                                    uVar20 = FUN_005d6ee0(iVar5);
                                    uVar13 = FUN_005d6ee0(iVar5);
                                  }
                                  else {
                                    uVar20 = FUN_005d6ea8(iVar5);
                                    uVar13 = FUN_005d6ea8(iVar5);
                                    local_3ece = '\0';
                                  }
                                  uVar20 = FT_DivFix(uVar13,uVar20);
                                  FUN_005d6e7c(iVar5,uVar20);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0xe) {
                                  iVar19 = FUN_005d6ee0(iVar5);
                                  if (iVar19 == -0x80000000) {
                                    FUN_005d6e7c(iVar5,0x7fffffff);
                                  }
                                  else {
                                    FUN_005d6e7c(iVar5,-iVar19);
                                  }
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0xf) {
                                  iVar19 = FUN_005d6ee0(iVar5);
                                  iVar14 = FUN_005d6ee0(iVar5);
                                  FUN_005d6e50(iVar5,iVar14 == iVar19);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x10) {
                                  if (*(char *)(local_30 + 2) != '\0') {
                                    iVar14 = FUN_005d6ea8(iVar5);
                                    iVar15 = FUN_005d6ea8(iVar5);
                                    iVar9 = FUN_005d6e44(iVar5);
                                    iVar9 = iVar9 - iVar15;
                                    uVar12 = 0;
                                    uVar16 = 0;
                                    local_3ec8 = 0;
                                    if (iVar14 == 0) {
                                      if (iVar15 == 3) {
                                        if ((local_3ecf != '\0') &&
                                           ((*(int *)(iVar21 + 0x1d4) == 0 ||
                                            (*(int *)(iVar21 + 0x1d8) != 7)))) goto LAB_005d5eba;
                                        FUN_005d6e7c(iVar5,param_6);
                                        FUN_005d6e7c(iVar5,param_7);
                                        uVar12 = 2;
                                        goto LAB_005d509c;
                                      }
                                    }
                                    else if (iVar14 == 1) {
                                      if (iVar15 == 0) {
                                        uVar12 = uVar16;
                                        if (local_3ecf != '\0') {
                                          iVar14 = FUN_005d185e(iVar21,6);
                                          if (iVar14 != 0) goto LAB_005d5034;
                                          *(undefined4 *)(iVar21 + 0x1d4) = 1;
                                          *(undefined4 *)(iVar21 + 0x1d8) = 0;
                                        }
                                        goto LAB_005d509c;
                                      }
                                    }
                                    else if (iVar14 == 2) {
                                      if (iVar15 == 0) {
                                        uVar12 = uVar16;
                                        if (local_3ecf != '\0') {
                                          if (*(int *)(iVar21 + 0x1d4) == 0) {
                                            iVar19 = 0x12;
                                            goto LAB_005d5034;
                                          }
                                          iVar19 = *(int *)(iVar21 + 0x1d8);
                                          *(int *)(iVar21 + 0x1d8) = iVar19 + 1;
                                          if (iVar19 - 1U < 6) {
                                            iVar14 = FUN_005d185e(iVar21,1);
                                            if (iVar14 != 0) {
                                              iVar19 = 0x12;
                                              goto LAB_005d5034;
                                            }
                                            iVar14 = iVar19;
                                            if (3 < iVar19) {
                                              iVar14 = iVar19 + -3;
                                            }
                                            auStack_3e30[iVar14 * 2 + 4] = param_6;
                                            auStack_3e30[iVar14 * 2 + 5] = param_7;
                                            if ((iVar19 == 3) || (iVar19 == 6)) {
                                              FUN_005d4912(auStack_2ebc,auStack_3e30[6],
                                                           auStack_3e30[7],auStack_3e30[8],
                                                           auStack_3e30[9],auStack_3e30[10],
                                                           auStack_3e30[0xb]);
                                            }
                                          }
                                        }
                                        goto LAB_005d509c;
                                      }
                                    }
                                    else if (iVar14 == 3) {
                                      if (iVar15 == 1) {
                                        if (local_3ecf != '\0') {
                                          FUN_005d23ac(auStack_3e78);
                                          FUN_005d23ac(auStack_3e58);
                                          FUN_005d4afe(auStack_3e94,local_3ecc);
                                          local_3e90 = 0;
                                          local_3e8f = 1;
                                        }
                                        uVar12 = 1;
                                        goto LAB_005d509c;
                                      }
                                    }
                                    else {
                                      if (iVar14 - 0xcU < 2) {
                                        FUN_005d709c(iVar5);
                                        uVar12 = uVar16;
                                        goto LAB_005d509c;
                                      }
                                      if (iVar14 - 0xeU < 5) {
                                        puVar10 = *(uint **)(iVar21 + 0x280);
                                        if (puVar10 == (uint *)0x0) {
                                          iVar19 = 0x12;
                                          goto LAB_005d5034;
                                        }
                                        uVar12 = (iVar14 + (uint)(iVar14 == 0x12)) - 0xd;
                                        if (iVar15 != *puVar10 * uVar12) {
                                          iVar19 = 0x12;
                                          goto LAB_005d5034;
                                        }
                                        iVar19 = uVar12 + iVar9;
                                        for (uVar16 = 0; uVar16 < uVar12; uVar16 = uVar16 + 1) {
                                          iVar14 = FUN_005d6f38(iVar5,iVar9);
                                          for (uVar23 = 1; uVar23 < *puVar10; uVar23 = uVar23 + 1) {
                                            uVar20 = FUN_005d6f38(iVar5,iVar19);
                                            iVar19 = iVar19 + 1;
                                            iVar11 = FT_MulFix(uVar20,*(undefined4 *)
                                                                       (puVar10[0x22] + uVar23 * 4))
                                            ;
                                            iVar14 = iVar11 + iVar14;
                                          }
                                          FUN_005d6f9e(iVar5,iVar9,iVar14);
                                          iVar9 = iVar9 + 1;
                                        }
                                        FUN_005d6fcc(iVar5,iVar15 - uVar12);
                                        goto LAB_005d509c;
                                      }
                                      if (iVar14 == 0x13) {
                                        piVar22 = *(int **)(iVar21 + 0x280);
                                        if ((((iVar15 == 1) && (piVar22 != (int *)0x0)) &&
                                            (iVar19 = FUN_005d6ea8(iVar5), -1 < iVar19)) &&
                                           ((uint)(*piVar22 + iVar19) <= *(uint *)(iVar21 + 0x288)))
                                        {
                                          FUN_00439be4(*(int *)(iVar21 + 0x284) + iVar19 * 4,
                                                       piVar22[0x22],*piVar22 << 2);
                                          uVar12 = uVar16;
                                          goto LAB_005d509c;
                                        }
                                      }
                                      else if (iVar14 == 0x14) {
                                        if (iVar15 == 2) {
                                          iVar19 = FUN_005d6ee0(iVar5);
                                          iVar14 = FUN_005d6ee0(iVar5);
                                          FUN_005d6e7c(iVar5,iVar19 + iVar14);
                                          uVar12 = 1;
                                          goto LAB_005d509c;
                                        }
                                      }
                                      else if (iVar14 == 0x15) {
                                        if (iVar15 == 2) {
                                          iVar19 = FUN_005d6ee0(iVar5);
                                          iVar14 = FUN_005d6ee0(iVar5);
                                          FUN_005d6e7c(iVar5,iVar14 - iVar19);
                                          uVar12 = 1;
                                          goto LAB_005d509c;
                                        }
                                      }
                                      else if (iVar14 == 0x16) {
                                        if (iVar15 == 2) {
                                          uVar20 = FUN_005d6ee0(iVar5);
                                          uVar13 = FUN_005d6ee0(iVar5);
                                          uVar20 = FT_MulFix(uVar13,uVar20);
                                          FUN_005d6e7c(iVar5,uVar20);
                                          uVar12 = 1;
                                          goto LAB_005d509c;
                                        }
                                      }
                                      else if (iVar14 == 0x17) {
                                        if (iVar15 == 2) {
                                          iVar19 = FUN_005d6ee0(iVar5);
                                          uVar20 = FUN_005d6ee0(iVar5);
                                          if (iVar19 != 0) {
                                            uVar20 = FT_DivFix(uVar20,iVar19);
                                            FUN_005d6e7c(iVar5,uVar20);
                                            uVar12 = 1;
                                            goto LAB_005d509c;
                                          }
                                        }
                                      }
                                      else if (iVar14 == 0x18) {
                                        if (((iVar15 == 2) && (*(int *)(iVar21 + 0x280) != 0)) &&
                                           ((uVar12 = FUN_005d6ea8(iVar5), -1 < (int)uVar12 &&
                                            (uVar12 < *(uint *)(iVar21 + 0x288))))) {
                                          uVar20 = FUN_005d6ee0(iVar5);
                                          *(undefined4 *)(*(int *)(iVar21 + 0x284) + uVar12 * 4) =
                                               uVar20;
                                          uVar12 = uVar16;
                                          goto LAB_005d509c;
                                        }
                                      }
                                      else if (iVar14 == 0x19) {
                                        if (((iVar15 == 1) && (*(int *)(iVar21 + 0x280) != 0)) &&
                                           ((uVar12 = FUN_005d6ea8(iVar5), -1 < (int)uVar12 &&
                                            (uVar12 < *(uint *)(iVar21 + 0x288))))) {
                                          FUN_005d6e7c(iVar5,*(undefined4 *)
                                                              (*(int *)(iVar21 + 0x284) + uVar12 * 4
                                                              ));
                                          uVar12 = 1;
                                          goto LAB_005d509c;
                                        }
                                      }
                                      else if (iVar14 == 0x1b) {
                                        if (iVar15 == 4) {
                                          iVar19 = FUN_005d6ee0(iVar5);
                                          iVar14 = FUN_005d6ee0(iVar5);
                                          uVar13 = FUN_005d6ee0(iVar5);
                                          uVar20 = FUN_005d6ee0(iVar5);
                                          if (iVar19 < iVar14) {
                                            uVar20 = uVar13;
                                          }
                                          FUN_005d6e7c(iVar5,uVar20);
                                          uVar12 = 1;
                                          goto LAB_005d509c;
                                        }
                                      }
                                      else if (iVar14 == 0x1c) {
                                        if (iVar15 == 0) {
                                          uVar12 = *(uint *)(*(int *)(iVar21 + 0x218) + 0x288);
                                          uVar20 = FUN_005d1d1c(*(undefined4 *)
                                                                 (*(int *)(iVar21 + 0x218) + 0x288))
                                          ;
                                          *(undefined4 *)(*(int *)(iVar21 + 0x218) + 0x288) = uVar20
                                          ;
                                          FUN_005d6e7c(iVar5,(uVar12 & 0xffff) + 1);
                                          uVar12 = 1;
                                          goto LAB_005d509c;
                                        }
                                      }
                                      else if ((-1 < iVar15) && (-1 < iVar14)) {
                                        if (3 < iVar15) {
                                          iVar15 = 3;
                                        }
                                        local_3ec8 = iVar15;
                                        for (iVar19 = 1; iVar19 <= iVar15; iVar19 = iVar19 + 1) {
                                          uVar16 = FUN_005d6ee0(iVar5);
                                          auStack_3e30[(local_3ec8 - iVar19) + 0xc] = uVar16;
                                        }
                                        goto LAB_005d509c;
                                      }
                                    }
                                    iVar19 = 0x12;
                                    goto LAB_005d5034;
                                  }
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x11) {
                                  if (*(char *)(local_30 + 2) != '\0') {
                                    if ((int)uVar12 < 1) {
                                      if (local_3ec8 == 0) {
                                        iVar19 = 0x12;
                                        goto LAB_005d5034;
                                      }
                                      iVar19 = local_3ec8 + 0xb;
                                      local_3ec8 = local_3ec8 + -1;
                                      FUN_005d6e7c(iVar5,auStack_3e30[iVar19]);
                                    }
                                    else {
                                      uVar12 = uVar12 - 1;
                                    }
                                  }
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x12) {
                                  FUN_005d6ee0(iVar5);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x14) {
                                  uVar16 = FUN_005d6ea8(iVar5);
                                  uVar20 = FUN_005d6ee0(iVar5);
                                  if (uVar16 < 0x20) {
                                    auStack_b4[uVar16] = uVar20;
                                  }
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x15) {
                                  uVar16 = FUN_005d6ea8(iVar5);
                                  if (uVar16 < 0x20) {
                                    FUN_005d6e7c(iVar5,auStack_b4[uVar16]);
                                  }
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x16) {
                                  iVar19 = FUN_005d6ee0(iVar5);
                                  iVar14 = FUN_005d6ee0(iVar5);
                                  uVar13 = FUN_005d6ee0(iVar5);
                                  uVar20 = FUN_005d6ee0(iVar5);
                                  if (iVar19 < iVar14) {
                                    uVar20 = uVar13;
                                  }
                                  FUN_005d6e7c(iVar5,uVar20);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x17) {
                                  uVar16 = *(uint *)(*(int *)(iVar21 + 0x218) + 0x288);
                                  uVar20 = FUN_005d1d1c(*(undefined4 *)
                                                         (*(int *)(iVar21 + 0x218) + 0x288));
                                  *(undefined4 *)(*(int *)(iVar21 + 0x218) + 0x288) = uVar20;
                                  FUN_005d6e7c(iVar5,(uVar16 & 0xffff) + 1);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x18) {
                                  uVar20 = FUN_005d6ee0(iVar5);
                                  uVar13 = FUN_005d6ee0(iVar5);
                                  uVar20 = FT_MulFix(uVar13,uVar20);
                                  FUN_005d6e7c(iVar5,uVar20);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x1a) {
                                  iVar19 = FUN_005d6ee0(iVar5);
                                  if (iVar19 < 1) {
                                    iVar14 = 0;
                                  }
                                  else {
                                    iVar15 = iVar19;
                                    if (9 < iVar19) {
                                      iVar15 = iVar19 >> 1;
                                    }
                                    do {
                                      iVar14 = FT_DivFix(iVar19,iVar15);
                                      iVar14 = iVar14 + iVar15 + 1 >> 1;
                                      bVar27 = iVar14 != iVar15;
                                      iVar15 = iVar14;
                                    } while (bVar27);
                                  }
                                  FUN_005d6e7c(iVar5,iVar14);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x1b) {
                                  uVar20 = FUN_005d6ee0(iVar5);
                                  FUN_005d6e7c(iVar5,uVar20);
                                  FUN_005d6e7c(iVar5,uVar20);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x1c) {
                                  uVar20 = FUN_005d6ee0(iVar5);
                                  uVar13 = FUN_005d6ee0(iVar5);
                                  FUN_005d6e7c(iVar5,uVar20);
                                  FUN_005d6e7c(iVar5,uVar13);
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x1d) {
                                  uVar16 = FUN_005d6ea8(iVar5);
                                  uVar23 = FUN_005d6e44(iVar5);
                                  if (uVar23 != 0) {
                                    if ((int)uVar16 < 0) {
                                      iVar19 = uVar23 - 1;
                                    }
                                    else if (uVar16 < uVar23) {
                                      iVar19 = (uVar23 - 1) - uVar16;
                                    }
                                    else {
                                      iVar19 = 0;
                                    }
                                    uVar20 = FUN_005d6f38(iVar5,iVar19);
                                    FUN_005d6e7c(iVar5,uVar20);
                                  }
                                  goto LAB_005d509c;
                                }
                                if (bVar2 == 0x1e) {
                                  uVar20 = FUN_005d6ea8(iVar5);
                                  uVar13 = FUN_005d6ea8(iVar5);
                                  FUN_005d6ff2(iVar5,uVar13,uVar20);
                                  goto LAB_005d509c;
                                }
                                if (((bVar2 == 0x21) && (*(char *)(local_30 + 2) != '\0')) &&
                                   (local_3ecf != '\0')) {
                                  param_7 = FUN_005d6ee0(iVar5);
                                  param_6 = FUN_005d6ee0(iVar5);
                                  *(undefined4 *)(iVar21 + 0x1d4) = 0;
                                }
                              }
                            }
                          }
                        }
                        else {
                          local_3ec8 = 0;
                        }
                      }
                    }
                  }
                }
                else {
                  if (bVar2 < 0xc) {
                    if (local_3ed4 < 1) {
                      iVar19 = 0x12;
                      goto LAB_005d5034;
                    }
                    local_3ed4 = local_3ed4 + -1;
                    iVar6 = FUN_005d23ba(auStack_3e38,local_3ed4);
                    goto LAB_005d509c;
                  }
                  if (bVar2 == 0xe) {
                    if ((*(char *)(local_30 + 2) == '\0') || (local_3ecf != '\0')) {
                      iVar6 = FUN_005d6e44(iVar5);
                      if (((iVar6 == 1) || (iVar6 = FUN_005d6e44(iVar5), iVar6 == 5)) &&
                         (local_3ed0 == false)) {
                        iVar6 = FUN_005d6f38(iVar5,0);
                        *param_8 = local_3eb4 + iVar6;
                      }
                      local_3ed0 = true;
                      if (((*(char *)(iVar21 + 0x224) == '\0') &&
                          (FUN_005d4a94(auStack_2ebc), *(char *)((int)local_30 + 9) == '\0')) &&
                         ((*(char *)(local_30 + 2) == '\0' &&
                          (uVar12 = FUN_005d6e44(iVar5), 1 < uVar12)))) {
                        if (param_5 == '\0') {
                          uVar20 = FUN_005d6ea8(iVar5);
                          uVar13 = FUN_005d6ea8(iVar5);
                          param_7 = FUN_005d6ee0(iVar5);
                          param_6 = FUN_005d6ee0(iVar5);
                          iVar19 = FUN_005d3362(iVar21,uVar20,&local_3eb4);
                          if (iVar19 == 0) {
                            FUN_005d4ed0(local_30,&local_3eb4,local_2c,local_28,1,param_6,param_7,
                                         &local_3ed4);
                            FUN_005d33be(iVar21,&local_3eb4);
                            iVar19 = FUN_005d3362(iVar21,uVar13,&local_3eb4);
                            if (iVar19 == 0) {
                              FUN_005d4ed0(local_30,&local_3eb4,local_2c,local_28,1,0,0,&local_3ed4)
                              ;
                              FUN_005d33be(iVar21,&local_3eb4);
                              iVar19 = iVar7;
                            }
                          }
                        }
                        else {
                          iVar19 = 0x12;
                        }
                      }
                      goto LAB_005d5034;
                    }
                    FUN_005d4754(auStack_2ebc,param_6,param_7);
                    local_3ecf = '\x01';
                    FUN_005d23ac(auStack_3e78);
                    FUN_005d23ac(auStack_3e58);
                    FUN_005d4afe(auStack_3e94,local_3ecc);
                    local_3e90 = 0;
                    local_3e8f = 1;
                    while (0 < local_3ed4) {
                      local_3ed4 = local_3ed4 + -1;
                      iVar6 = FUN_005d23ba(auStack_3e38,local_3ed4);
                    }
                    *(undefined4 *)(iVar6 + 0xc) = *(undefined4 *)(iVar6 + 4);
                  }
                  else if (bVar2 < 0xe) {
                    if (*(char *)(local_30 + 2) != '\0') {
                      uVar20 = FUN_005d6ee0(iVar5);
                      **(undefined4 **)(iVar21 + 0x24) = uVar20;
                      *(undefined4 *)(*(int *)(iVar21 + 0x24) + 4) = 0;
                      iVar14 = FUN_005d6ee0(iVar5);
                      **(int **)(iVar21 + 0x20) = iVar14 + **(int **)(iVar21 + 0x20);
                      local_3ed0 = true;
                      if (*(char *)(iVar21 + 0x2f) != '\0') goto LAB_005d5034;
                      if (local_3ecf != '\0') {
                        param_6 = iVar14 + param_6;
                      }
                    }
                  }
                  else if (bVar2 == 0x10) {
                    if (*(char *)((int)local_30 + 9) != '\0') {
                      if (local_30[0x18] == 0) {
                        iVar19 = 0x12;
                        goto LAB_005d5034;
                      }
                      iVar19 = (**(code **)(local_30[0x89] + 0xc))
                                         (local_30 + 0x17,local_30[0x1e],local_30[0x1f],
                                          local_30[0x20]);
                      if ((iVar19 != 0) &&
                         (iVar7 = (**(code **)(local_30[0x89] + 0x10))
                                            (local_30 + 0x17,local_30[0x1e],local_30[0x1f],
                                             local_30[0x20]), iVar19 = iVar7, iVar7 != 0))
                      goto LAB_005d5034;
                      uVar16 = FUN_005d6ea8(iVar5);
                      if (local_3eac < uVar16) {
                        iVar19 = 0x12;
                        goto LAB_005d5034;
                      }
                      FUN_005d4e40(local_30 + 0x17,iVar5,uVar16);
                      *(undefined1 *)((int)local_30 + 0x5d) = 1;
                      goto LAB_005d509c;
                    }
                  }
                  else if (bVar2 < 0x10) {
                    if (*(char *)((int)local_30 + 9) != '\0') {
                      if (*(char *)((int)local_30 + 0x5d) != '\0') {
                        iVar19 = 0x12;
                        goto LAB_005d5034;
                      }
                      iVar19 = FUN_005d6ea8(iVar5);
                      if (-1 < iVar19) {
                        local_30[0x1e] = iVar19;
                      }
                    }
                  }
                  else {
                    if (bVar2 == 0x12) goto LAB_005d5368;
                    if (0x11 < bVar2) {
                      if ((bVar2 == 0x14) || (bVar2 < 0x14)) {
                        uVar16 = FUN_005d6e44(iVar5);
                        if ((uVar16 < 2) || (iVar14 = FUN_005d4b14(auStack_3e94), iVar14 == 0)) {
                          FUN_005d4bba(local_30,iVar5,auStack_3e78,param_8,&local_3ed0,0);
                          if (*(char *)(iVar21 + 0x224) != '\0') goto LAB_005d5034;
                          if (bVar2 == 0x13) {
                            iVar19 = FUN_005d23b2(auStack_3e58);
                            iVar14 = FUN_005d23b2(auStack_3e78);
                            FUN_005d4b4c(auStack_3e94,iVar6,iVar14 + iVar19);
                          }
                          else {
                            FUN_005d36b8(auStack_3dd8,local_30,auStack_107c,auStack_160,local_3ea8);
                            FUN_005d4afe(auStack_3df4,local_3ecc);
                            iVar19 = FUN_005d23b2(auStack_3e58);
                            iVar14 = FUN_005d23b2(auStack_3e78);
                            FUN_005d4b4c(auStack_3df4,iVar6,iVar14 + iVar19);
                            FUN_005d3c0a(auStack_3dd8,auStack_3e58,auStack_3e78,auStack_3df4,0,0);
                          }
                        }
                      }
                      else {
                        if (bVar2 == 0x16) {
                          uVar16 = FUN_005d6e44(iVar5);
                          if ((1 < uVar16) && (local_3ed0 == false)) {
                            iVar14 = FUN_005d6f38(iVar5,0);
                            *param_8 = local_3eb4 + iVar14;
                          }
                          local_3ed0 = true;
                          if (*(char *)(iVar21 + 0x224) == '\0') {
                            iVar19 = FUN_005d6ee0(iVar5);
                            param_6 = iVar19 + param_6;
                            if (*(int *)(iVar21 + 0x1d4) == 0) {
                              FUN_005d4754(auStack_2ebc,param_6,param_7);
                            }
                            goto LAB_005d68b2;
                          }
                          goto LAB_005d5034;
                        }
                        if (0x15 < bVar2) {
                          if (bVar2 == 0x18) goto LAB_005d55a6;
                          if (bVar2 < 0x18) goto LAB_005d53c4;
                          if (bVar2 == 0x1a) {
                            uVar16 = FUN_005d6e44(iVar5);
                            local_3ec4 = uVar16 & 0xfffffffd;
                            for (uVar16 = uVar16 - local_3ec4; uVar16 < local_3ec4;
                                uVar16 = uVar16 + 4) {
                              uVar23 = param_6;
                              if ((int)((local_3ec4 - uVar16) * -0x80000000) < 0) {
                                iVar19 = FUN_005d6f38(iVar5,uVar16);
                                uVar16 = uVar16 + 1;
                                uVar23 = param_6 + iVar19;
                              }
                              iVar19 = FUN_005d6f38(iVar5,uVar16);
                              local_3ebc = param_7 + iVar19;
                              iVar19 = FUN_005d6f38(iVar5,uVar16 + 1);
                              uVar25 = uVar23 + iVar19;
                              iVar19 = FUN_005d6f38(iVar5,uVar16 + 2);
                              iVar19 = local_3ebc + iVar19;
                              local_3ec0 = uVar25;
                              iVar14 = FUN_005d6f38(iVar5,uVar16 + 3);
                              uVar26 = iVar19 + iVar14;
                              FUN_005d4912(auStack_2ebc,uVar23,local_3ebc,uVar25,iVar19,local_3ec0,
                                           uVar26);
                              param_6 = local_3ec0;
                              param_7 = uVar26;
                            }
                            FUN_005d709c(iVar5);
                          }
                          else if (bVar2 < 0x1a) {
                            local_3ebc = FUN_005d6e44(iVar5);
                            for (uVar16 = 0; uVar16 + 6 < local_3ebc; uVar16 = uVar16 + 2) {
                              iVar19 = FUN_005d6f38(iVar5,uVar16);
                              param_6 = iVar19 + param_6;
                              iVar19 = FUN_005d6f38(iVar5,uVar16 + 1);
                              param_7 = iVar19 + param_7;
                              FUN_005d47d4(auStack_2ebc,param_6,param_7);
                            }
                            for (; uVar16 < local_3ebc; uVar16 = uVar16 + 6) {
                              iVar19 = FUN_005d6f38(iVar5,uVar16);
                              local_3ec0 = param_6 + iVar19;
                              iVar19 = FUN_005d6f38(iVar5,uVar16 + 1);
                              local_3ec4 = param_7 + iVar19;
                              iVar19 = FUN_005d6f38(iVar5,uVar16 + 2);
                              iVar19 = local_3ec0 + iVar19;
                              iVar14 = FUN_005d6f38(iVar5,uVar16 + 3);
                              iVar14 = local_3ec4 + iVar14;
                              iVar15 = FUN_005d6f38(iVar5,uVar16 + 4);
                              uVar25 = iVar19 + iVar15;
                              iVar15 = FUN_005d6f38(iVar5,uVar16 + 5);
                              uVar23 = iVar14 + iVar15;
                              FUN_005d4912(auStack_2ebc,local_3ec0,local_3ec4,iVar19,iVar14,uVar25,
                                           uVar23);
                              param_6 = uVar25;
                              param_7 = uVar23;
                            }
                            FUN_005d709c(iVar5);
                          }
                          else {
                            if (bVar2 != 0x1c) {
                              if (bVar2 < 0x1c) {
                                uVar16 = FUN_005d6e44(iVar5);
                                local_3ec4 = uVar16 & 0xfffffffd;
                                for (uVar16 = uVar16 - local_3ec4; uVar16 < local_3ec4;
                                    uVar16 = uVar16 + 4) {
                                  uVar23 = param_7;
                                  if ((int)((local_3ec4 - uVar16) * -0x80000000) < 0) {
                                    iVar19 = FUN_005d6f38(iVar5,uVar16);
                                    uVar16 = uVar16 + 1;
                                    uVar23 = param_7 + iVar19;
                                  }
                                  iVar19 = FUN_005d6f38(iVar5,uVar16);
                                  local_3ebc = param_6 + iVar19;
                                  iVar19 = FUN_005d6f38(iVar5,uVar16 + 1);
                                  iVar19 = local_3ebc + iVar19;
                                  iVar14 = FUN_005d6f38(iVar5,uVar16 + 2);
                                  uVar25 = uVar23 + iVar14;
                                  iVar14 = FUN_005d6f38(iVar5,uVar16 + 3);
                                  uVar26 = iVar19 + iVar14;
                                  local_3ec0 = uVar25;
                                  FUN_005d4912(auStack_2ebc,local_3ebc,uVar23,iVar19,uVar25,uVar26,
                                               uVar25);
                                  param_7 = local_3ec0;
                                  param_6 = uVar26;
                                }
                                FUN_005d709c(iVar5);
                                goto LAB_005d509c;
                              }
                              if (bVar2 != 0x1e) {
                                if (bVar2 < 0x1e) goto LAB_005d56da;
                                if (bVar2 != 0x1f) {
                                  if (bVar2 < 0xf7) {
                                    FUN_005d6e50(iVar5,bVar2 - 0x8b);
                                  }
                                  else if (bVar2 < 0xfb) {
                                    iVar19 = FUN_005d6d98(iVar6);
                                    FUN_005d6e50(iVar5,iVar19 + (bVar2 - 0xf7) * 0x100 + 0x6c);
                                  }
                                  else if (bVar2 == 0xff) {
                                    iVar19 = FUN_005d6d98(iVar6);
                                    iVar14 = FUN_005d6d98(iVar6);
                                    iVar15 = FUN_005d6d98(iVar6);
                                    uVar16 = FUN_005d6d98(iVar6);
                                    if (*(char *)(local_30 + 2) == '\0') {
                                      FUN_005d6e7c(iVar5);
                                    }
                                    else {
                                      if ((64000 < (uVar16 | iVar14 << 0x10 | iVar19 << 0x18 |
                                                             iVar15 << 8) + 32000) &&
                                         (local_3ece == '\0')) {
                                        local_3ece = '\x01';
                                      }
                                      FUN_005d6e50(iVar5);
                                    }
                                  }
                                  else {
                                    iVar19 = FUN_005d6d98(iVar6);
                                    FUN_005d6e50(iVar5,-0x6c - (iVar19 + (bVar2 - 0xfb) * 0x100));
                                  }
                                  goto LAB_005d509c;
                                }
                              }
                              uVar16 = FUN_005d6e44(iVar5);
                              uVar23 = (uint)(bVar2 == 0x1f);
                              local_3eb8 = uVar16 & 0xfffffffd;
                              for (uVar16 = uVar16 - local_3eb8; uVar16 < local_3eb8;
                                  uVar16 = uVar16 + 4) {
                                if ((char)uVar23 == '\0') {
                                  local_3ec0 = param_6;
                                  iVar19 = FUN_005d6f38(iVar5,uVar16);
                                  local_3ebc = param_7 + iVar19;
                                  iVar19 = FUN_005d6f38(iVar5,uVar16 + 1);
                                  uVar24 = local_3ec0 + iVar19;
                                  iVar19 = FUN_005d6f38(iVar5,uVar16 + 2);
                                  local_3ec4 = local_3ebc + iVar19;
                                  iVar19 = FUN_005d6f38(iVar5,uVar16 + 3);
                                  uVar26 = uVar24 + iVar19;
                                  uVar25 = local_3ec4;
                                  if (local_3eb8 - uVar16 == 5) {
                                    iVar19 = FUN_005d6f38(iVar5,uVar16 + 4);
                                    uVar16 = uVar16 + 1;
                                    uVar25 = local_3ec4 + iVar19;
                                  }
                                  uVar23 = 1;
                                }
                                else {
                                  iVar19 = FUN_005d6f38(iVar5,uVar16);
                                  local_3ec0 = param_6 + iVar19;
                                  local_3ebc = param_7;
                                  iVar19 = FUN_005d6f38(iVar5,uVar16 + 1);
                                  uVar24 = local_3ec0 + iVar19;
                                  iVar19 = FUN_005d6f38(iVar5,uVar16 + 2);
                                  local_3ec4 = local_3ebc + iVar19;
                                  iVar19 = FUN_005d6f38(iVar5,uVar16 + 3);
                                  uVar25 = local_3ec4 + iVar19;
                                  uVar26 = uVar24;
                                  if (local_3eb8 - uVar16 == 5) {
                                    iVar19 = FUN_005d6f38(iVar5,uVar16 + 4);
                                    uVar16 = uVar16 + 1;
                                    uVar26 = uVar24 + iVar19;
                                  }
                                  uVar23 = 0;
                                }
                                FUN_005d4912(auStack_2ebc,local_3ec0,local_3ebc,uVar24,local_3ec4,
                                             uVar26,uVar25);
                                param_6 = uVar26;
                                param_7 = uVar25;
                              }
                              FUN_005d709c(iVar5);
                              goto LAB_005d509c;
                            }
                            sVar3 = FUN_005d6d98(iVar6);
                            uVar4 = FUN_005d6d98(iVar6);
                            FUN_005d6e50(iVar5,(int)(short)(uVar4 | sVar3 << 8));
                          }
                          goto LAB_005d509c;
                        }
                        uVar16 = FUN_005d6e44(iVar5);
                        if ((2 < uVar16) && (local_3ed0 == false)) {
                          iVar14 = FUN_005d6f38(iVar5,0);
                          *param_8 = local_3eb4 + iVar14;
                        }
                        local_3ed0 = true;
                        if (*(char *)(iVar21 + 0x224) != '\0') goto LAB_005d5034;
                        iVar19 = FUN_005d6ee0(iVar5);
                        param_7 = iVar19 + param_7;
                        iVar19 = FUN_005d6ee0(iVar5);
                        param_6 = iVar19 + param_6;
                        if (*(int *)(iVar21 + 0x1d4) == 0) {
                          FUN_005d4754(auStack_2ebc,param_6,param_7);
                        }
                      }
                    }
                  }
                }
                goto LAB_005d68b2;
              }
            }
            uVar16 = FUN_005d6e44(iVar5);
            bVar27 = bVar2 != 6;
            for (uVar23 = 0; bVar27 = !bVar27, uVar23 < uVar16; uVar23 = uVar23 + 1) {
              iVar19 = FUN_005d6f38(iVar5,uVar23);
              if (bVar27) {
                param_6 = iVar19 + param_6;
              }
              else {
                param_7 = iVar19 + param_7;
              }
              FUN_005d47d4(auStack_2ebc,param_6,param_7);
            }
            FUN_005d709c(iVar5);
            goto LAB_005d509c;
          }
LAB_005d53c4:
          if ((*(char *)(local_30 + 2) != '\0') ||
             (iVar14 = FUN_005d4b14(auStack_3e94), iVar14 == 0)) {
            if (*(char *)(local_30 + 2) == '\0') {
              uVar20 = 0;
            }
            else {
              uVar20 = **(undefined4 **)(iVar21 + 0x20);
            }
            FUN_005d4bba(local_30,iVar5,auStack_3e78,param_8,&local_3ed0,uVar20);
            cVar1 = *(char *)(iVar21 + 0x224);
            goto joined_r0x005d59e8;
          }
        }
      }
LAB_005d68b2:
      FUN_005d709c(iVar5);
      goto LAB_005d509c;
    }
  }
LAB_005d5034:
  FUN_005d2a0a(local_3ecc,iVar19);
  FUN_005d4032(auStack_2ebc);
  FUN_005d230e(auStack_3e78);
  FUN_005d230e(auStack_3e58);
  FUN_005d230e(auStack_3e38);
  FUN_005d6e22(iVar5);
  return;
LAB_005d5eba:
  iVar19 = 0x12;
  goto LAB_005d5034;
}

