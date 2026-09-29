
/* WARNING: Type propagation algorithm not settling */

int FUN_004d1638(code *param_1,undefined4 param_2,byte *param_3,undefined4 *param_4,int param_5)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  byte *pbVar4;
  int *piVar5;
  undefined1 auVar6 [4];
  char *pcVar7;
  char cVar8;
  byte bVar9;
  byte *pbVar10;
  uint uVar11;
  undefined4 uVar12;
  undefined4 *puVar13;
  undefined2 *puVar14;
  undefined8 *puVar15;
  undefined1 *puVar16;
  uint uVar17;
  uint uVar18;
  int iVar19;
  char *pcVar20;
  char *pcVar21;
  int iVar22;
  byte bVar23;
  undefined4 *puVar24;
  bool bVar25;
  bool bVar26;
  undefined8 uVar27;
  undefined4 local_90;
  int *local_8c;
  byte *local_88;
  int local_84;
  int local_80;
  int local_7c;
  undefined4 local_78;
  byte local_74;
  byte local_73;
  char local_72;
  undefined1 local_71;
  undefined1 local_70 [4];
  int local_6c;
  char local_68 [23];
  undefined4 auStack_51 [9];
  undefined4 *local_2c;
  undefined4 *puStack_28;
  
  uVar18 = 0xffffffff;
  local_8c = (int *)*param_4;
  local_2c = auStack_51;
  local_71 = (undefined1)param_5;
  iVar22 = -1;
  local_84 = 0;
  local_90 = param_2;
  local_88 = param_3;
  puStack_28 = param_4;
  do {
    iVar3 = FUN_004d58ae(*local_88);
    pbVar4 = local_88;
    if (iVar3 == 0) {
      if (*local_88 == 0) goto LAB_004d169a;
      if (*local_88 == 0x25) {
        if (local_88[1] == 0x2a) {
          local_74 = local_88[1];
          local_88 = local_88 + 2;
        }
        else {
          local_74 = 0;
          local_88 = local_88 + 1;
        }
        local_7c = 0;
        for (; *local_88 - 0x30 < 10; local_88 = local_88 + 1) {
          if (local_7c < DAT_004d2100) {
            pbVar4 = (byte *)(local_7c * 5);
            local_7c = (uint)*local_88 + local_7c * 10 + -0x30;
          }
        }
        local_78 = 0xffffffff;
        uVar27 = FUN_00481818(s_hjltzL_004d2104,*local_88);
        local_73 = 0;
        if ((int)uVar27 != 0) {
          local_73 = *local_88;
          local_88 = local_88 + 1;
        }
        if (local_73 == 0x68) {
          if (*local_88 == 0x68) {
            local_73 = 0x62;
            pbVar10 = local_88;
LAB_004d174e:
            local_88 = pbVar10 + 1;
          }
        }
        else {
          pbVar10 = (byte *)((ulonglong)uVar27 >> 0x20);
          bVar23 = local_73;
          if (local_73 == 0x6c) {
            bVar23 = *local_88;
            pbVar10 = local_88;
          }
          if (local_73 == 0x6c && bVar23 == 0x6c) {
            local_73 = 0x71;
            goto LAB_004d174e;
          }
        }
        iVar3 = FUN_00481818(&DAT_004d2300,*local_88);
        if (iVar3 == 0) {
          do {
            local_84 = local_84 + 1;
            pbVar4 = (byte *)(*param_1)(local_90,0,1);
            iVar3 = FUN_004d58ae();
          } while (iVar3 != 0);
          FUN_004d161c(param_1,&local_90,pbVar4);
        }
        local_72 = '\0';
        uVar11 = (uint)*local_88;
        if (uVar11 == 0x25) {
          local_84 = local_84 + 1;
          iVar3 = (*param_1)(local_90,0,1);
          if (iVar3 == 0x25) goto LAB_004d181a;
          FUN_004d161c(param_1,&local_90,iVar3);
          if (iVar3 == -1) {
LAB_004d1f9e:
            iVar3 = -1;
          }
          else {
LAB_004d20ec:
            iVar3 = 0;
          }
LAB_004d20ee:
          if (iVar22 < 0) {
            iVar22 = iVar3;
          }
          goto LAB_004d169e;
        }
        if ((uVar11 == 0x41) || (uVar11 - 0x45 < 3)) {
LAB_004d18d2:
          local_80 = local_7c;
          if (local_7c < 1) {
            local_80 = 0x7fffffff;
          }
          auVar6 = (undefined1  [4])FUN_004d15fa(param_1,&local_90);
          iVar3 = 0;
          puVar16 = (undefined1 *)register0x00000054;
          if (auVar6 == (undefined1  [4])0x2b || auVar6 == (undefined1  [4])0x2d) {
            local_68[0] = SUB41(auVar6,0);
            auVar6 = (undefined1  [4])FUN_004d15fa(param_1,&local_90);
            puVar16 = (undefined1 *)((int)&param_5 + 1);
          }
          pcVar7 = puVar16 + -0x68;
          cVar8 = false;
          bVar23 = 10;
          if (auVar6 == (undefined1  [4])0x30) {
            auVar6 = (undefined1  [4])FUN_004d15fa(param_1,&local_90);
            bVar25 = ((uint)auVar6 & 0xff | 0x20) == 0x78;
            pcVar20 = pcVar7;
            if (bVar25) {
              *pcVar7 = '0';
              puVar16[-0x67] = 0x78;
              auVar6 = (undefined1  [4])FUN_004d15fa(param_1,&local_90);
              bVar23 = 0x10;
              pcVar20 = puVar16 + -0x66;
            }
            cVar8 = !bVar25;
            while (auVar6 == (undefined1  [4])0x30) {
              local_80 = local_80 + -1;
              if (local_80 < 0) {
                local_84 = local_84 + 1;
                auVar6 = (undefined1  [4])uVar18;
              }
              else {
                auVar6 = (undefined1  [4])FUN_004d15e8(param_1,&local_90);
              }
              cVar8 = true;
            }
            pcVar7 = pcVar20;
            if ((bool)cVar8 != false) {
              pcVar7 = pcVar20 + 1;
              *pcVar20 = '0';
            }
LAB_004d1b1e:
            iVar19 = 0;
            while (cVar1 = SUB41(auVar6,0), auVar6 != (undefined1  [4])0xffffffff) {
              uVar11 = (uint)auVar6 & 0xff;
              if (uVar11 < 0x61) {
                if (uVar11 < 0x41) {
                  if (uVar11 - 0x30 < 10) {
                    bVar9 = cVar1 - 0x30;
                  }
                  else {
                    bVar9 = 0xff;
                  }
                }
                else {
                  bVar9 = cVar1 - 0x37;
                }
              }
              else {
                bVar9 = cVar1 + 0xa9;
              }
              if (bVar23 <= bVar9) break;
              if (iVar19 < 0x24) {
                *pcVar7 = cVar1;
                iVar19 = iVar19 + 1;
                pcVar7 = pcVar7 + 1;
              }
              else {
                iVar3 = iVar3 + 1;
              }
              local_80 = local_80 + -1;
              if (local_80 < 0) {
                local_84 = local_84 + 1;
                auVar6 = (undefined1  [4])uVar18;
              }
              else {
                auVar6 = (undefined1  [4])FUN_004d15e8(param_1,&local_90);
              }
              cVar8 = true;
            }
            local_70[0] = cVar8;
            local_6c = iVar19;
            iVar19 = FUN_004d43a8();
            pcVar20 = pcVar7;
            if (auVar6 == (undefined1  [4])(uint)**(byte **)(iVar19 + 0x24)) {
              pcVar20 = pcVar7 + 1;
              *pcVar7 = cVar1;
              local_84 = local_84 + 1;
              local_80 = local_80 + -1;
              if (local_80 < 0) {
                auVar6 = (undefined1  [4])0xffffffff;
              }
              else {
                auVar6 = (undefined1  [4])(*param_1)(local_90,0,1);
              }
            }
            pcVar7 = pcVar20;
            if (local_6c == 0) {
              uVar11 = (uint)local_70 & 0xff;
              while (auVar6 == (undefined1  [4])0x30) {
                iVar3 = iVar3 + -1;
                local_80 = local_80 + -1;
                if (local_80 < 0) {
                  local_84 = local_84 + 1;
                  auVar6 = (undefined1  [4])uVar18;
                }
                else {
                  auVar6 = (undefined1  [4])FUN_004d15e8(param_1,&local_90);
                }
                uVar11 = 1;
              }
              local_70[0] = (char)uVar11;
              if (iVar3 < 0) {
                pcVar7 = pcVar20 + 1;
                *pcVar20 = '0';
                iVar3 = iVar3 + 1;
              }
            }
            iVar19 = local_6c;
            cVar8 = local_70[0];
            while (cVar1 = SUB41(auVar6,0), auVar6 != (undefined1  [4])0xffffffff) {
              uVar11 = (uint)auVar6 & 0xff;
              if (uVar11 < 0x61) {
                if (uVar11 < 0x41) {
                  if (uVar11 - 0x30 < 10) {
                    bVar9 = cVar1 - 0x30;
                  }
                  else {
                    bVar9 = 0xff;
                  }
                }
                else {
                  bVar9 = cVar1 - 0x37;
                }
              }
              else {
                bVar9 = cVar1 + 0xa9;
              }
              if (bVar23 <= bVar9) break;
              pcVar20 = pcVar7;
              if (iVar19 < 0x24) {
                pcVar20 = pcVar7 + 1;
                *pcVar7 = cVar1;
                iVar19 = iVar19 + 1;
              }
              local_80 = local_80 + -1;
              if (local_80 < 0) {
                local_84 = local_84 + 1;
                auVar6 = (undefined1  [4])uVar18;
              }
              else {
                auVar6 = (undefined1  [4])FUN_004d15e8(param_1,&local_90);
              }
              cVar8 = '\x01';
              pcVar7 = pcVar20;
            }
            if (cVar8 != '\0') {
              uVar11 = (uint)auVar6 & 0xff | 0x20;
              if (bVar23 == 10) {
                if (uVar11 == 0x65) {
LAB_004d1cd4:
                  pcVar21 = pcVar7 + 1;
                  *pcVar7 = cVar1;
                  local_80 = local_80 + -1;
                  pcVar20 = pcVar21;
                  if (local_80 < 0) {
LAB_004d1d02:
                    local_84 = local_84 + 1;
                    auVar6 = (undefined1  [4])0xffffffff;
                  }
                  else {
                    local_84 = local_84 + 1;
                    auVar6 = (undefined1  [4])(*param_1)(local_90,0,1);
                    if (auVar6 == (undefined1  [4])0x2b || auVar6 == (undefined1  [4])0x2d) {
                      pcVar20 = pcVar7 + 2;
                      *pcVar21 = SUB41(auVar6,0);
                      local_80 = local_80 + -1;
                      if (local_80 < 0) goto LAB_004d1d02;
                      local_84 = local_84 + 1;
                      auVar6 = (undefined1  [4])(*param_1)(local_90,0,1);
                    }
                  }
                  cVar8 = '\0';
                  while (auVar6 == (undefined1  [4])0x30) {
                    local_80 = local_80 + -1;
                    if (local_80 < 0) {
                      local_84 = local_84 + 1;
                      auVar6 = (undefined1  [4])uVar18;
                    }
                    else {
                      auVar6 = (undefined1  [4])FUN_004d15e8(param_1,&local_90);
                    }
                    cVar8 = '\x01';
                  }
                  pcVar7 = pcVar20;
                  if (cVar8 != '\0') {
                    pcVar7 = pcVar20 + 1;
                    *pcVar20 = '0';
                  }
                  iVar19 = 0;
                  while ((int)auVar6 - 0x30U < 10) {
                    pcVar20 = pcVar7;
                    if (iVar19 < 8) {
                      pcVar20 = pcVar7 + 1;
                      *pcVar7 = SUB41(auVar6,0);
                      iVar19 = iVar19 + 1;
                    }
                    local_80 = local_80 + -1;
                    if (local_80 < 0) {
                      local_84 = local_84 + 1;
                      auVar6 = (undefined1  [4])uVar18;
                    }
                    else {
                      auVar6 = (undefined1  [4])FUN_004d15e8(param_1,&local_90);
                    }
                    cVar8 = '\x01';
                    pcVar7 = pcVar20;
                  }
                }
              }
              else if (uVar11 == 0x70) goto LAB_004d1cd4;
            }
LAB_004d1c70:
            FUN_004d161c(param_1,&local_90,auVar6);
            pcVar20 = pcVar7;
            if (cVar8 == '\0') {
              if (pcVar7 == local_68 && auVar6 == (undefined1  [4])0xffffffff) goto LAB_004d1f9e;
              goto LAB_004d20ec;
            }
          }
          else {
            bVar9 = SUB41(auVar6,0) | 0x20;
            if (bVar9 != 0x6e) {
              if (bVar9 != 0x69) goto LAB_004d1b1e;
              *pcVar7 = 'i';
              auVar6 = (undefined1  [4])FUN_004d15fa(param_1,&local_90);
              bVar23 = 0;
              pcVar7 = puVar16 + -0x67;
              if (((uint)auVar6 & 0xff | 0x20) == 0x6e) {
                pcVar7 = puVar16 + -0x66;
                puVar16[-0x67] = 'n';
                auVar6 = (undefined1  [4])FUN_004d15fa(param_1,&local_90);
                if (((uint)auVar6 & 0xff | 0x20) == 0x66) {
                  uVar11 = FUN_004d15fa(param_1,&local_90);
                  if ((uVar11 & 0xff | 0x20) != 0x69) {
                    FUN_004d161c(param_1,&local_90,uVar11);
                    uVar2 = 0x66;
                    goto LAB_004d1a3e;
                  }
                  local_84 = local_84 + 1;
                  local_80 = local_80 + -1;
                  if (local_80 < 0) {
                    auVar6 = (undefined1  [4])0xffffffff;
                  }
                  else {
                    auVar6 = (undefined1  [4])(*param_1)(local_90,0,1);
                  }
                  if (((uint)auVar6 & 0xff | 0x20) == 0x6e) {
                    local_84 = local_84 + 1;
                    local_80 = local_80 + -1;
                    if (local_80 < 0) {
                      auVar6 = (undefined1  [4])0xffffffff;
                    }
                    else {
                      auVar6 = (undefined1  [4])(*param_1)(local_90,0,1);
                    }
                    if (((uint)auVar6 & 0xff | 0x20) == 0x69) {
                      local_84 = local_84 + 1;
                      local_80 = local_80 + -1;
                      if (local_80 < 0) {
                        auVar6 = (undefined1  [4])0xffffffff;
                      }
                      else {
                        auVar6 = (undefined1  [4])(*param_1)(local_90,0,1);
                      }
                      if (((uint)auVar6 & 0xff | 0x20) == 0x74) {
                        local_84 = local_84 + 1;
                        local_80 = local_80 + -1;
                        if (local_80 < 0) {
                          auVar6 = (undefined1  [4])0xffffffff;
                        }
                        else {
                          auVar6 = (undefined1  [4])(*param_1)(local_90,0,1);
                        }
                        if (((uint)auVar6 & 0xff | 0x20) == 0x79) {
                          pcVar20 = puVar16 + -0x65;
                          *pcVar7 = 'f';
                          goto LAB_004d1c7c;
                        }
                      }
                    }
                  }
                }
              }
              goto LAB_004d1c70;
            }
            *pcVar7 = 'n';
            auVar6 = (undefined1  [4])FUN_004d15fa(param_1,&local_90);
            bVar23 = 0;
            pcVar7 = puVar16 + -0x67;
            if (((uint)auVar6 & 0xff | 0x20) != 0x61) goto LAB_004d1c70;
            puVar16[-0x67] = 'a';
            auVar6 = (undefined1  [4])FUN_004d15fa(param_1,&local_90);
            pcVar7 = puVar16 + -0x66;
            if (((uint)auVar6 & 0xff | 0x20) != 0x6e) goto LAB_004d1c70;
            iVar19 = FUN_004d15fa(param_1,&local_90);
            if (iVar19 == 0x28) {
              do {
                local_80 = local_80 + -1;
                if (local_80 < 0) {
                  local_84 = local_84 + 1;
                  uVar11 = 0xffffffff;
                }
                else {
                  uVar11 = FUN_004d15e8(param_1,&local_90);
                }
                local_70 = (undefined1  [4])uVar11;
                iVar19 = FUN_00541ba8(uVar11);
              } while (((iVar19 != 0) || (uVar11 - 0x30 < 10)) ||
                      (local_70 == (undefined1  [4])0x5f));
              auVar6 = local_70;
              if (local_70 != (undefined1  [4])0x29) goto LAB_004d1c70;
              uVar2 = 0x6e;
            }
            else {
              FUN_004d161c(param_1,&local_90,iVar19);
              uVar2 = 0x6e;
            }
LAB_004d1a3e:
            bVar23 = 0;
            pcVar20 = puVar16 + -0x65;
            puVar16[-0x66] = uVar2;
          }
LAB_004d1c7c:
          *pcVar20 = '\0';
          if (local_74 == 0) {
            if (bVar23 < 0xb) {
              uVar27 = FUN_00541bc2(local_68,0,iVar3,0);
            }
            else {
              uVar27 = FUN_00541bc2(local_68,0,0,0);
              uVar27 = FUN_004d41f4((int)uVar27,(int)((ulonglong)uVar27 >> 0x20),iVar3 << 2);
            }
            local_72 = '\x01';
            if (local_73 == 0x6c) {
              piVar5 = local_8c + 1;
              puVar15 = (undefined8 *)*local_8c;
              local_8c = piVar5;
              if (puVar15 != (undefined8 *)0x0) {
LAB_004d1d8c:
                local_72 = '\x01';
                *puVar15 = uVar27;
                goto LAB_004d181a;
              }
              pcVar7 = (char *)((int)&DAT_004d20fc + DAT_004d20fc);
            }
            else if (local_73 == 0x4c) {
              piVar5 = local_8c + 1;
              puVar15 = (undefined8 *)*local_8c;
              local_8c = piVar5;
              if (puVar15 != (undefined8 *)0x0) goto LAB_004d1d8c;
              pcVar7 = (char *)((int)&DAT_004d20fc + DAT_004d20fc);
            }
            else {
              puVar13 = (undefined4 *)*local_8c;
              local_8c = local_8c + 1;
              if (puVar13 != (undefined4 *)0x0) {
                uVar12 = FUN_00541bca();
                *puVar13 = uVar12;
                goto LAB_004d181a;
              }
              pcVar7 = (char *)((int)&DAT_004d20fc + DAT_004d20fc);
            }
LAB_004d20ce:
            iVar3 = FUN_004d40a0(pcVar7);
            iVar3 = -1 - iVar3;
            goto LAB_004d20e2;
          }
        }
        else {
          if (uVar11 == 0x58) goto LAB_004d1dc8;
          if (uVar11 != 0x5b) {
            if (uVar11 == 0x61) goto LAB_004d18d2;
            if (uVar11 == 99) {
              uVar12 = 0;
              goto LAB_004d20d8;
            }
            if (uVar11 == 100) goto LAB_004d1dc8;
            if (uVar11 - 0x65 < 3) goto LAB_004d18d2;
            if (uVar11 != 0x69) {
              if (uVar11 != 0x6e) {
                if (1 < uVar11 - 0x6f) {
                  if (uVar11 == 0x73) {
                    uVar12 = 1;
                    goto LAB_004d20d8;
                  }
                  if ((uVar11 != 0x75) && (uVar11 != 0x78)) goto LAB_004d20ec;
                }
                goto LAB_004d1dc8;
              }
              if (local_74 != 0) goto LAB_004d181a;
              if (local_73 == 0x62) {
                if ((undefined1 *)*local_8c == (undefined1 *)0x0) {
                  pcVar7 = s_scanf_s__bad__n_argument_004d2308;
                  local_8c = local_8c + 1;
                  goto LAB_004d20ce;
                }
                *(undefined1 *)*local_8c = (char)local_84;
                local_8c = local_8c + 1;
                goto LAB_004d181a;
              }
              if (local_73 == 0x68) {
                if ((undefined2 *)*local_8c == (undefined2 *)0x0) {
                  pcVar7 = s_scanf_s__bad__n_argument_004d2308;
                  local_8c = local_8c + 1;
                  goto LAB_004d20ce;
                }
                *(undefined2 *)*local_8c = (short)local_84;
                local_8c = local_8c + 1;
                goto LAB_004d181a;
              }
              if ((local_73 == 0x6a) || ((local_73 != 0x6c && (local_73 == 0x71)))) {
                piVar5 = (int *)*local_8c;
                if (piVar5 == (int *)0x0) {
                  pcVar7 = s_scanf_s__bad__n_argument_004d2308;
                  local_8c = local_8c + 1;
                  goto LAB_004d20ce;
                }
                *piVar5 = local_84;
                piVar5[1] = local_84 >> 0x1f;
                local_8c = local_8c + 1;
                goto LAB_004d181a;
              }
              if ((int *)*local_8c != (int *)0x0) {
                *(int *)*local_8c = local_84;
                local_8c = local_8c + 1;
                goto LAB_004d181a;
              }
              pcVar7 = s_scanf_s__bad__n_argument_004d2308;
              local_8c = local_8c + 1;
              goto LAB_004d20ce;
            }
LAB_004d1dc8:
            local_80 = DAT_004d22fc;
            if (0 < local_7c) {
              local_80 = local_7c + -1;
            }
            puVar13 = (undefined4 *)local_70;
            if (local_80 < 0) {
              local_84 = local_84 + 1;
LAB_004d1e1c:
              uVar11 = 0xffffffff;
            }
            else {
              local_84 = local_84 + 1;
              uVar11 = (*param_1)(local_90,0,1);
              if (uVar11 == 0x2b || uVar11 == 0x2d) {
                local_70[0] = (char)uVar11;
                puVar13 = (undefined4 *)(local_70 + 1);
                local_84 = local_84 + 1;
                local_80 = local_80 + -1;
                if (local_80 < 0) goto LAB_004d1e1c;
                uVar11 = (*param_1)(local_90,0,1);
              }
            }
            bVar25 = false;
            bVar23 = *local_88;
            if (bVar23 == 100 || bVar23 == 0x75) {
              pbVar4 = (byte *)0xa;
            }
            else if (bVar23 == 0x69) {
              pbVar4 = (byte *)0x0;
            }
            else if (bVar23 == 0x6f) {
              pbVar4 = &NMI;
            }
            else {
              bVar26 = bVar23 != 0x70;
              if (bVar26) {
                bVar23 = bVar23 | 0x20;
              }
              if (!bVar26 || bVar23 == 0x78) {
                pbVar4 = &MemManage;
              }
            }
            if (uVar11 == 0x30) {
              bVar25 = true;
              local_80 = local_80 + -1;
              if (local_80 < 0) {
                local_84 = local_84 + 1;
                uVar11 = 0xffffffff;
              }
              else {
                local_84 = local_84 + 1;
                uVar11 = (*param_1)(local_90,0,1);
              }
              if ((uVar11 & 0xff | 0x20) != 0x78) {
                if (pbVar4 == (byte *)0x0) {
                  pbVar4 = &NMI;
                }
LAB_004d1ebe:
                while (uVar11 == 0x30) {
                  local_80 = local_80 + -1;
                  if (local_80 < 0) {
                    local_84 = local_84 + 1;
                    uVar11 = uVar18;
                  }
                  else {
                    uVar11 = FUN_004d15e8(param_1,&local_90);
                  }
                  bVar25 = true;
                }
                if (bVar25) {
                  *(undefined1 *)puVar13 = 0x30;
                  puVar13 = (undefined4 *)((int)puVar13 + 1);
                }
                goto LAB_004d1f20;
              }
              if (pbVar4 != (byte *)0x0 && pbVar4 != &MemManage) goto LAB_004d1ebe;
              pbVar4 = &MemManage;
              local_80 = local_80 + -1;
              if (-1 < local_80) {
                local_84 = local_84 + 1;
                uVar11 = (*param_1)(local_90,0,1);
                bVar25 = false;
                goto LAB_004d1ebe;
              }
              local_84 = local_84 + 1;
              uVar11 = 0xffffffff;
              bVar25 = false;
              puVar24 = puVar13;
            }
            else {
              if (pbVar4 == (byte *)0x0) {
                pbVar4 = (byte *)0xa;
              }
LAB_004d1f20:
              while (puVar24 = puVar13, uVar11 != 0xffffffff) {
                uVar17 = uVar11 & 0xff;
                if (uVar17 < 0x61) {
                  if (uVar17 < 0x41) {
                    if (uVar17 - 0x30 < 10) {
                      uVar17 = uVar11 - 0x30;
                    }
                    else {
                      uVar17 = 0xff;
                    }
                  }
                  else {
                    uVar17 = uVar11 - 0x37;
                  }
                }
                else {
                  uVar17 = uVar11 - 0x57;
                }
                if (((uint)pbVar4 & 0xff) <= (uVar17 & 0xff)) break;
                if (puVar13 < local_2c) {
                  puVar24 = (undefined4 *)((int)puVar13 + 1);
                  *(char *)puVar13 = (char)uVar11;
                }
                local_80 = local_80 + -1;
                if (local_80 < 0) {
                  local_84 = local_84 + 1;
                  bVar25 = true;
                  uVar11 = 0xffffffff;
                  break;
                }
                local_84 = local_84 + 1;
                uVar11 = (*param_1)(local_90,0,1);
                bVar25 = true;
                puVar13 = puVar24;
              }
            }
            FUN_004d161c(param_1,&local_90,uVar11);
            if (!bVar25) {
              if (puVar24 == (undefined4 *)local_70 && uVar11 == 0xffffffff) goto LAB_004d1f9e;
              goto LAB_004d20ec;
            }
            *(undefined1 *)puVar24 = 0;
            if (local_74 == 0) {
              if (*local_88 != 100 && *local_88 != 0x69) {
                uVar27 = FUN_00541d84(local_70,0,pbVar4);
                uVar12 = (undefined4)uVar27;
                if (*local_88 == 0x70) {
                  puVar13 = (undefined4 *)*local_8c;
                  goto joined_r0x004d2098;
                }
                if (local_73 == 0x62) goto LAB_004d2022;
                if (local_73 == 0x68) goto LAB_004d1fd6;
                if (local_73 != 0x6a) {
                  if (local_73 == 0x6c) {
                    puVar13 = (undefined4 *)*local_8c;
                  }
                  else {
                    if (local_73 == 0x71) {
                      puVar15 = (undefined8 *)*local_8c;
                      goto joined_r0x004d200c;
                    }
                    if (local_73 == 0x74) {
                      puVar13 = (undefined4 *)*local_8c;
                    }
                    else if (local_73 == 0x7a) {
                      puVar13 = (undefined4 *)*local_8c;
                    }
                    else {
                      puVar13 = (undefined4 *)*local_8c;
                    }
                  }
                  goto joined_r0x004d2098;
                }
                puVar15 = (undefined8 *)*local_8c;
                goto joined_r0x004d200c;
              }
              uVar27 = FUN_00541e2c(local_70,0,pbVar4);
              uVar12 = (undefined4)uVar27;
              if (local_73 == 0x62) {
LAB_004d2022:
                local_72 = '\x01';
                piVar5 = local_8c + 1;
                puVar16 = (undefined1 *)*local_8c;
                local_8c = piVar5;
                if (puVar16 != (undefined1 *)0x0) {
                  *puVar16 = (char)uVar12;
                  goto LAB_004d181a;
                }
code_r0x004d20cc:
                local_72 = '\x01';
                pcVar7 = s_scanf_s__bad_integer_argument_004d2344;
                goto LAB_004d20ce;
              }
              if (local_73 == 0x68) {
LAB_004d1fd6:
                local_72 = '\x01';
                piVar5 = local_8c + 1;
                puVar14 = (undefined2 *)*local_8c;
                local_8c = piVar5;
                if (puVar14 != (undefined2 *)0x0) {
                  *puVar14 = (short)uVar12;
                  goto LAB_004d181a;
                }
                goto code_r0x004d20cc;
              }
              if (local_73 != 0x6a) {
                if (local_73 == 0x6c) {
                  puVar13 = (undefined4 *)*local_8c;
                }
                else {
                  if (local_73 == 0x71) {
                    puVar15 = (undefined8 *)*local_8c;
                    goto joined_r0x004d200c;
                  }
                  if (local_73 == 0x74) {
                    puVar13 = (undefined4 *)*local_8c;
                  }
                  else if (local_73 == 0x7a) {
                    puVar13 = (undefined4 *)*local_8c;
                  }
                  else {
                    puVar13 = (undefined4 *)*local_8c;
                  }
                }
joined_r0x004d2098:
                local_8c = (int *)((int)local_8c + 4);
                if (puVar13 != (undefined4 *)0x0) {
                  local_72 = '\x01';
                  *puVar13 = uVar12;
                  goto LAB_004d181a;
                }
                goto code_r0x004d20cc;
              }
              puVar15 = (undefined8 *)*local_8c;
joined_r0x004d200c:
              local_8c = (int *)((int)local_8c + 4);
              if (puVar15 == (undefined8 *)0x0) goto code_r0x004d20cc;
              goto LAB_004d1d8c;
            }
            goto LAB_004d181a;
          }
          uVar12 = 0xffffffff;
LAB_004d20d8:
          iVar3 = FUN_004d2158(param_1,&local_90,uVar12);
LAB_004d20e2:
          if (iVar3 < 1) {
            if ((param_5 != 0) && (iVar3 == -0x23)) {
              return -1;
            }
            goto LAB_004d20ee;
          }
        }
LAB_004d181a:
        if (iVar22 < 0) {
          iVar22 = 0;
        }
        if (local_72 != '\0') {
          iVar22 = iVar22 + 1;
        }
      }
      else {
        local_84 = local_84 + 1;
        uVar11 = (*param_1)(local_90,0,1);
        if (uVar11 != *pbVar4) {
          FUN_004d161c(param_1,&local_90,uVar11);
LAB_004d169a:
          iVar3 = 0;
          if (0 < iVar22) {
LAB_004d169e:
            iVar3 = iVar22;
          }
          return iVar3;
        }
      }
    }
    else {
      do {
        local_84 = local_84 + 1;
        uVar12 = (*param_1)(local_90,0,1);
        iVar3 = FUN_004d58ae();
      } while (iVar3 != 0);
      FUN_004d161c(param_1,&local_90,uVar12);
    }
    local_88 = local_88 + 1;
  } while( true );
}

