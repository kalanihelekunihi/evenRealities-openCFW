
void af_latin_metrics_init_blues(int *param_1,int param_2)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  short *local_228;
  int local_224;
  int local_220;
  int local_21c;
  int local_218;
  int *local_214;
  int local_210;
  int local_20c;
  uint local_208;
  uint local_204;
  int local_200;
  int local_1fc;
  char *local_1f8;
  uint local_1f4;
  uint local_1f0;
  int local_1ec [2];
  short local_1e4;
  short sStack_1e2;
  int local_1e0;
  int local_1dc;
  int local_1d8;
  uint local_1d0;
  uint local_1cc;
  int aiStack_1c4 [51];
  int aiStack_f8 [51];
  int *local_2c;
  int local_28;
  
  local_214 = param_1 + 0x917;
  local_228 = (short *)(DAT_005a96f8 + (uint)*(byte *)(*param_1 + 3) * 4);
  local_1cc = (uint)param_1[10] / 0xe;
  local_2c = param_1;
  local_28 = param_2;
  local_1ec[0] = af_shaper_buf_create(param_2);
  do {
    if (*local_228 == 0x1469) {
      af_shaper_buf_destroy(local_28,local_1ec[0]);
      if (local_214[0x36] != 0) {
        for (uVar4 = 0; uVar4 < (uint)local_214[0x36]; uVar4 = uVar4 + 1) {
          local_1ec[uVar4] = (int)(local_214 + uVar4 * 9 + 0x37);
        }
        af_latin_sort_blue(local_214[0x36],local_1ec);
        for (uVar4 = 0; uVar4 < local_214[0x36] - 1U; uVar4 = uVar4 + 1) {
          if ((*(byte *)(local_1ec[uVar4] + 0x20) & 6) == 0) {
            piVar5 = (int *)local_1ec[uVar4];
          }
          else {
            piVar5 = (int *)(local_1ec[uVar4] + 0xc);
          }
          if ((*(byte *)(local_1ec[uVar4 + 1] + 0x20) & 6) == 0) {
            piVar7 = (int *)local_1ec[uVar4 + 1];
          }
          else {
            piVar7 = (int *)(local_1ec[uVar4 + 1] + 0xc);
          }
          if (*piVar7 < *piVar5) {
            *piVar5 = *piVar7;
          }
        }
      }
      return;
    }
    local_1f8 = (char *)(DAT_005a96fc + *local_228);
    local_204 = 0;
    local_208 = 0;
    iVar9 = 0;
    iVar10 = 0;
    while (*local_1f8 != '\0') {
      bVar2 = false;
      for (; *local_1f8 == ' '; local_1f8 = local_1f8 + 1) {
      }
      local_1f8 = (char *)af_shaper_get_cluster(local_1f8,local_2c,local_1ec[0],&local_1f0);
      if (local_1f0 != 0) {
        if ((int)((uint)*(byte *)(local_228 + 1) << 0x1f) < 0) {
          local_218 = -0x80000000;
        }
        else {
          local_218 = 0x7fffffff;
        }
        local_1f4 = 0;
LAB_005a8e5e:
        if (local_1f4 < local_1f0) {
          bVar1 = false;
          iVar3 = af_shaper_get_elem(local_2c,local_1ec[0],local_1f4,0,&local_224);
          if (iVar3 != 0) {
            iVar3 = FT_Load_Glyph(local_28,iVar3,1);
            FUN_00439c04(&local_1e4,*(int *)(local_28 + 0x54) + 0x6c,0x14);
            if ((iVar3 != 0) || (sStack_1e2 < 3)) goto LAB_005a8e58;
            iVar6 = 0;
            iVar3 = 0;
            local_20c = 0;
            iVar17 = 0;
            iVar12 = -1;
            for (iVar11 = 0; iVar11 < local_1e4; iVar11 = iVar11 + 1) {
              iVar14 = (int)*(short *)(local_1d8 + iVar11 * 2);
              iVar8 = iVar12;
              if (iVar17 < iVar14) {
                iVar15 = iVar17;
                if ((*(byte *)(local_228 + 1) & 3) == 0) {
                  for (; iVar15 <= iVar14; iVar15 = iVar15 + 1) {
                    if ((iVar8 < 0) || (*(int *)(local_1e0 + iVar15 * 8 + 4) < iVar6)) {
                      iVar6 = *(int *)(local_1e0 + iVar15 * 8 + 4);
                      iVar8 = iVar15;
                      if (local_224 + iVar6 <= iVar10) {
                        iVar10 = local_224 + iVar6;
                      }
                    }
                    else if (iVar9 <= local_224 + *(int *)(local_1e0 + iVar15 * 8 + 4)) {
                      iVar9 = local_224 + *(int *)(local_1e0 + iVar15 * 8 + 4);
                    }
                  }
                }
                else {
                  for (; iVar15 <= iVar14; iVar15 = iVar15 + 1) {
                    if ((iVar8 < 0) || (iVar6 < *(int *)(local_1e0 + iVar15 * 8 + 4))) {
                      iVar6 = *(int *)(local_1e0 + iVar15 * 8 + 4);
                      iVar8 = iVar15;
                      if (iVar9 <= local_224 + iVar6) {
                        iVar9 = local_224 + iVar6;
                      }
                    }
                    else if (local_224 + *(int *)(local_1e0 + iVar15 * 8 + 4) <= iVar10) {
                      iVar10 = local_224 + *(int *)(local_1e0 + iVar15 * 8 + 4);
                    }
                  }
                }
                if (iVar8 != iVar12) {
                  iVar3 = iVar17;
                  local_20c = iVar14;
                }
              }
              iVar17 = iVar14 + 1;
              iVar12 = iVar8;
            }
            if (-1 < iVar12) {
              iVar17 = *(int *)(local_1e0 + iVar12 * 8);
              iVar11 = iVar12;
              local_21c = iVar12;
              local_220 = iVar12;
              if ((*(byte *)(local_1dc + iVar12) & 3) != 1) {
                local_220 = -1;
                iVar11 = local_220;
              }
              do {
                iVar8 = local_20c;
                if (iVar3 < local_21c) {
                  iVar8 = local_21c + -1;
                }
                if (*(int *)(local_1e0 + iVar8 * 8 + 4) - iVar6 < 0) {
                  iVar14 = iVar6 - *(int *)(local_1e0 + iVar8 * 8 + 4);
                }
                else {
                  iVar14 = *(int *)(local_1e0 + iVar8 * 8 + 4) - iVar6;
                }
                local_210 = iVar12;
                if (5 < iVar14) {
                  if (*(int *)(local_1e0 + iVar8 * 8) - iVar17 < 0) {
                    iVar15 = iVar17 - *(int *)(local_1e0 + iVar8 * 8);
                  }
                  else {
                    iVar15 = *(int *)(local_1e0 + iVar8 * 8) - iVar17;
                  }
                  if (iVar15 <= iVar14 * 0x14) break;
                }
                if (((*(byte *)(local_1dc + iVar8) & 3) == 1) && (local_220 = iVar8, iVar11 < 0)) {
                  iVar11 = iVar8;
                }
                local_21c = iVar8;
              } while (iVar8 != iVar12);
              do {
                iVar8 = iVar3;
                if (local_210 < local_20c) {
                  iVar8 = local_210 + 1;
                }
                if (*(int *)(local_1e0 + iVar8 * 8 + 4) - iVar6 < 0) {
                  iVar14 = iVar6 - *(int *)(local_1e0 + iVar8 * 8 + 4);
                }
                else {
                  iVar14 = *(int *)(local_1e0 + iVar8 * 8 + 4) - iVar6;
                }
                if (5 < iVar14) {
                  if (*(int *)(local_1e0 + iVar8 * 8) - iVar17 < 0) {
                    iVar15 = iVar17 - *(int *)(local_1e0 + iVar8 * 8);
                  }
                  else {
                    iVar15 = *(int *)(local_1e0 + iVar8 * 8) - iVar17;
                  }
                  if (iVar15 <= iVar14 * 0x14) break;
                }
                if (((*(byte *)(local_1dc + iVar8) & 3) == 1) && (iVar11 = iVar8, local_220 < 0)) {
                  local_220 = iVar8;
                }
                local_210 = iVar8;
              } while (iVar8 != iVar12);
              if ((int)((uint)*(byte *)(local_228 + 1) << 0x1b) < 0) {
                local_1ec[1] = (uint)local_2c[10] / 0x19;
                if (*(int *)(local_1e0 + local_210 * 8) - *(int *)(local_1e0 + local_21c * 8) < 0) {
                  iVar14 = *(int *)(local_1e0 + local_21c * 8) - *(int *)(local_1e0 + local_210 * 8)
                  ;
                }
                else {
                  iVar14 = *(int *)(local_1e0 + local_210 * 8) - *(int *)(local_1e0 + local_21c * 8)
                  ;
                }
                if ((iVar14 < local_1ec[1]) && ((local_210 - local_21c) + 2 <= local_20c - iVar3)) {
                  local_1d0 = (uint)local_2c[10] >> 2;
                  local_200 = 0;
                  local_1fc = 0;
                  iVar14 = iVar12;
                  do {
                    iVar15 = local_20c;
                    if (iVar3 < iVar14) {
                      iVar15 = iVar14 + -1;
                    }
                  } while ((*(int *)(local_1e0 + iVar15 * 8) == iVar17) &&
                          (iVar14 = iVar15, iVar15 != iVar12));
                  if (iVar15 == iVar12) goto LAB_005a8e58;
                  bVar1 = false;
                  iVar17 = local_210;
                  iVar14 = local_210;
                  do {
                    if (!bVar1) {
                      local_1fc = iVar17;
                      if ((*(byte *)(local_1dc + iVar17) & 3) != 1) {
                        local_1fc = -1;
                      }
                      bVar1 = true;
                      iVar14 = iVar17;
                      local_200 = local_1fc;
                    }
                    iVar13 = iVar3;
                    if (iVar17 < local_20c) {
                      iVar13 = iVar17 + 1;
                    }
                    if (iVar6 - *(int *)(local_1e0 + iVar14 * 8 + 4) < 0) {
                      iVar17 = *(int *)(local_1e0 + iVar14 * 8 + 4) - iVar6;
                    }
                    else {
                      iVar17 = iVar6 - *(int *)(local_1e0 + iVar14 * 8 + 4);
                    }
                    if ((int)local_1d0 < iVar17) {
                      bVar1 = false;
                    }
                    else {
                      if (*(int *)(local_1e0 + iVar13 * 8 + 4) -
                          *(int *)(local_1e0 + iVar14 * 8 + 4) < 0) {
                        iVar17 = *(int *)(local_1e0 + iVar14 * 8 + 4) -
                                 *(int *)(local_1e0 + iVar13 * 8 + 4);
                      }
                      else {
                        iVar17 = *(int *)(local_1e0 + iVar13 * 8 + 4) -
                                 *(int *)(local_1e0 + iVar14 * 8 + 4);
                      }
                      if (5 < iVar17) {
                        if (*(int *)(local_1e0 + iVar13 * 8) - *(int *)(local_1e0 + iVar14 * 8) < 0)
                        {
                          iVar16 = *(int *)(local_1e0 + iVar14 * 8) -
                                   *(int *)(local_1e0 + iVar13 * 8);
                        }
                        else {
                          iVar16 = *(int *)(local_1e0 + iVar13 * 8) -
                                   *(int *)(local_1e0 + iVar14 * 8);
                        }
                        if (iVar16 <= iVar17 * 0x14) {
                          bVar1 = false;
                          goto LAB_005a9374;
                        }
                      }
                      if (((*(byte *)(local_1dc + iVar13) & 3) == 1) &&
                         (local_1fc = iVar13, local_200 < 0)) {
                        local_200 = iVar13;
                      }
                      if (*(int *)(local_1e0 + iVar13 * 8) - *(int *)(local_1e0 + iVar14 * 8) < 0) {
                        iVar16 = *(int *)(local_1e0 + iVar14 * 8) - *(int *)(local_1e0 + iVar13 * 8)
                        ;
                      }
                      else {
                        iVar16 = *(int *)(local_1e0 + iVar13 * 8) - *(int *)(local_1e0 + iVar14 * 8)
                        ;
                      }
                      if ((*(int *)(local_1e0 + iVar14 * 8) < *(int *)(local_1e0 + iVar13 * 8) ==
                           *(int *)(local_1e0 + iVar15 * 8) < *(int *)(local_1e0 + iVar12 * 8)) &&
                         (local_1ec[1] <= iVar16)) goto LAB_005a9402;
                    }
LAB_005a9374:
                    iVar17 = iVar13;
                  } while (iVar13 != local_21c);
                }
              }
              goto LAB_005a9428;
            }
            goto LAB_005a8e44;
          }
          goto LAB_005a8e58;
        }
        if ((local_218 != -0x80000000) && (local_218 != 0x7fffffff)) {
          if (bVar2) {
            aiStack_1c4[local_208] = local_218;
            local_208 = local_208 + 1;
          }
          else {
            aiStack_f8[local_204] = local_218;
            local_204 = local_204 + 1;
          }
        }
      }
    }
    if (local_204 != 0 || local_208 != 0) {
      af_sort_pos(local_208,aiStack_1c4);
      af_sort_pos(local_204,aiStack_f8);
      iVar3 = local_214[0x36];
      piVar5 = local_214 + iVar3 * 9 + 0x37;
      piVar7 = local_214 + iVar3 * 9 + 0x3a;
      local_214[0x36] = local_214[0x36] + 1;
      if (local_204 == 0) {
        *piVar7 = aiStack_1c4[local_208 >> 1];
        *piVar5 = *piVar7;
      }
      else if (local_208 == 0) {
        *piVar7 = aiStack_f8[local_204 >> 1];
        *piVar5 = *piVar7;
      }
      else {
        *piVar5 = aiStack_f8[local_204 >> 1];
        *piVar7 = aiStack_1c4[local_208 >> 1];
      }
      if (*piVar7 != *piVar5) {
        if (*piVar5 < *piVar7 != ((*(byte *)(local_228 + 1) & 3) != 0)) {
          *piVar7 = (*piVar5 + *piVar7) / 2;
          *piVar5 = *piVar7;
        }
      }
      local_214[iVar3 * 9 + 0x3d] = iVar9;
      local_214[iVar3 * 9 + 0x3e] = iVar10;
      local_214[iVar3 * 9 + 0x3f] = 0;
      if ((int)((uint)*(byte *)(local_228 + 1) << 0x1f) < 0) {
        local_214[iVar3 * 9 + 0x3f] = local_214[iVar3 * 9 + 0x3f] | 2;
      }
      if ((int)((uint)*(byte *)(local_228 + 1) << 0x1e) < 0) {
        local_214[iVar3 * 9 + 0x3f] = local_214[iVar3 * 9 + 0x3f] | 4;
      }
      if ((int)((uint)*(byte *)(local_228 + 1) << 0x1d) < 0) {
        local_214[iVar3 * 9 + 0x3f] = local_214[iVar3 * 9 + 0x3f] | 8;
      }
      if ((int)((uint)*(byte *)(local_228 + 1) << 0x1c) < 0) {
        local_214[iVar3 * 9 + 0x3f] = local_214[iVar3 * 9 + 0x3f] | 0x10;
      }
    }
    local_228 = local_228 + 2;
  } while( true );
  while( true ) {
    if (((*(byte *)(local_1dc + iVar12) & 3) == 1) && (local_200 < 0)) {
      local_200 = iVar12;
    }
    local_210 = iVar12;
    iVar13 = iVar12;
    local_1fc = iVar12;
    if (iVar12 == local_21c) break;
LAB_005a9402:
    iVar12 = iVar3;
    if (iVar13 < local_20c) {
      iVar12 = iVar13 + 1;
    }
    if (*(int *)(local_1e0 + iVar12 * 8 + 4) - *(int *)(local_1e0 + iVar14 * 8 + 4) < 0) {
      iVar6 = *(int *)(local_1e0 + iVar14 * 8 + 4) - *(int *)(local_1e0 + iVar12 * 8 + 4);
    }
    else {
      iVar6 = *(int *)(local_1e0 + iVar12 * 8 + 4) - *(int *)(local_1e0 + iVar14 * 8 + 4);
    }
    if (5 < iVar6) {
      if (*(int *)(local_1e0 + iVar8 * 8) - *(int *)(local_1e0 + iVar14 * 8) < 0) {
        iVar6 = *(int *)(local_1e0 + iVar14 * 8) - *(int *)(local_1e0 + iVar8 * 8);
      }
      else {
        iVar6 = *(int *)(local_1e0 + iVar8 * 8) - *(int *)(local_1e0 + iVar14 * 8);
      }
      if (iVar6 <= iVar17 * 0x14) {
        local_210 = local_20c;
        if (iVar3 < iVar12) {
          local_210 = iVar12 + -1;
        }
        break;
      }
    }
  }
  iVar6 = *(int *)(local_1e0 + iVar14 * 8 + 4);
  local_220 = local_200;
  iVar11 = local_1fc;
  local_21c = iVar14;
LAB_005a9428:
  iVar6 = local_224 + iVar6;
  if ((-1 < local_220) && (-1 < iVar11)) {
    if (*(int *)(local_1e0 + iVar11 * 8) - *(int *)(local_1e0 + local_220 * 8) < 0) {
      iVar3 = *(int *)(local_1e0 + local_220 * 8) - *(int *)(local_1e0 + iVar11 * 8);
    }
    else {
      iVar3 = *(int *)(local_1e0 + iVar11 * 8) - *(int *)(local_1e0 + local_220 * 8);
    }
    if ((int)local_1cc < iVar3) {
      bVar1 = false;
      goto LAB_005a9480;
    }
  }
  if (((*(byte *)(local_1dc + local_21c) & 3) == 1) && ((*(byte *)(local_1dc + local_210) & 3) == 1)
     ) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
LAB_005a9480:
  if ((!bVar1) || (-1 < (int)((uint)*(byte *)(local_228 + 1) << 0x1d))) {
LAB_005a8e44:
    if ((int)((uint)*(byte *)(local_228 + 1) << 0x1f) < 0) {
      if (local_218 < iVar6) {
        local_218 = iVar6;
        bVar2 = bVar1;
      }
    }
    else if (iVar6 < local_218) {
      local_218 = iVar6;
      bVar2 = bVar1;
    }
  }
LAB_005a8e58:
  local_1f4 = local_1f4 + 1;
  goto LAB_005a8e5e;
}

