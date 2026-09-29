
int TT_Vary_Apply_Glyph_Deltas(int param_1,uint param_2,int param_3,uint param_4)

{
  ushort uVar1;
  bool bVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;
  int iVar10;
  int *piVar11;
  int iVar12;
  uint *puVar13;
  int iVar14;
  uint uVar15;
  uint uVar16;
  int local_70;
  int local_6c;
  uint local_68;
  int local_64;
  int local_60;
  int local_5c;
  int local_58;
  int local_54;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  uint local_40;
  uint local_3c;
  uint local_38;
  int local_34;
  uint local_30;
  int local_28;
  
  piVar11 = *(int **)(param_1 + 0x68);
  local_6c = piVar11[7];
  puVar13 = *(uint **)(param_1 + 700);
  iVar10 = 0;
  local_60 = 0;
  local_48 = 0;
  local_4c = 0;
  local_40 = 0;
  local_50 = 0;
  iVar12 = 0;
  if ((*(char *)(param_1 + 0x2b9) == '\0') || (puVar13 == (uint *)0x0)) {
    local_70 = 6;
  }
  else if ((param_2 < puVar13[0x11]) &&
          (*(int *)(puVar13[0x12] + param_2 * 4) != *(int *)(puVar13[0x12] + param_2 * 4 + 4))) {
    local_28 = param_1;
    local_64 = ft_mem_realloc(local_6c,8,0,param_4,0,&local_70);
    if (((local_70 == 0) &&
        (iVar10 = ft_mem_realloc(local_6c,8,0,param_4,0,&local_70), local_70 == 0)) &&
       (local_60 = ft_mem_realloc(local_6c,1,0,param_4,0,&local_70), local_70 == 0)) {
      bVar2 = false;
    }
    else {
      bVar2 = true;
    }
    if (((!bVar2) &&
        (local_70 = FT_Stream_Seek(piVar11,*(undefined4 *)(puVar13[0x12] + param_2 * 4)),
        local_70 == 0)) &&
       (local_70 = FT_Stream_EnterFrame
                             (piVar11,*(int *)(puVar13[0x12] + param_2 * 4 + 4) -
                                      *(int *)(puVar13[0x12] + param_2 * 4)), local_70 == 0)) {
      iVar14 = piVar11[8];
      iVar4 = *piVar11;
      local_44 = ft_mem_realloc(local_6c,4,0,*puVar13,0,&local_70);
      if (((local_70 == 0) &&
          (local_48 = ft_mem_realloc(local_6c,4,0,*puVar13,0,&local_70), local_70 == 0)) &&
         (local_4c = ft_mem_realloc(local_6c,4,0,*puVar13,0,&local_70), local_70 == 0)) {
        bVar2 = false;
      }
      else {
        bVar2 = true;
      }
      if (!bVar2) {
        local_38 = FT_Stream_GetUShort(piVar11);
        iVar5 = FT_Stream_GetUShort(piVar11);
        if (puVar13[0x13] < (local_38 & 0xfff) * 4 + iVar5) {
          local_70 = 8;
        }
        else {
          uVar15 = (iVar14 - iVar4) + iVar5;
          if ((int)(local_38 << 0x10) < 0) {
            iVar14 = piVar11[8];
            iVar4 = *piVar11;
            if (uVar15 < (uint)(piVar11[9] - *piVar11)) {
              iVar5 = *piVar11 + uVar15;
            }
            else {
              iVar5 = piVar11[9];
            }
            piVar11[8] = iVar5;
            local_50 = ft_var_readpackedpoints(piVar11,puVar13[0x13],&local_40);
            uVar15 = piVar11[8] - *piVar11;
            if ((uint)(iVar14 - iVar4) < (uint)(piVar11[9] - *piVar11)) {
              iVar4 = *piVar11 + (iVar14 - iVar4);
            }
            else {
              iVar4 = piVar11[9];
            }
            piVar11[8] = iVar4;
          }
          for (uVar7 = 0; uVar7 < param_4; uVar7 = uVar7 + 1) {
            puVar8 = (undefined4 *)(*(int *)(param_3 + 4) + uVar7 * 8);
            uVar6 = puVar8[1];
            puVar9 = (undefined4 *)(local_64 + uVar7 * 8);
            *puVar9 = *puVar8;
            puVar9[1] = uVar6;
          }
          for (local_3c = 0; local_3c < (local_38 & 0xfff); local_3c = local_3c + 1) {
            local_34 = FT_Stream_GetUShort(piVar11);
            uVar7 = FT_Stream_GetUShort(piVar11);
            if ((int)(uVar7 << 0x10) < 0) {
              for (uVar16 = 0; uVar16 < *puVar13; uVar16 = uVar16 + 1) {
                sVar3 = FT_Stream_GetUShort(piVar11);
                *(int *)(local_44 + uVar16 * 4) = (int)sVar3 << 2;
              }
            }
            else {
              if (puVar13[0xf] <= (uVar7 & 0xfff)) {
                local_70 = 8;
                break;
              }
              FUN_00439be4(local_44,puVar13[0x10] + *puVar13 * (uVar7 & 0xfff) * 4,*puVar13 << 2);
            }
            if ((int)(uVar7 << 0x11) < 0) {
              for (uVar16 = 0; uVar16 < *puVar13; uVar16 = uVar16 + 1) {
                sVar3 = FT_Stream_GetUShort(piVar11);
                *(int *)(local_48 + uVar16 * 4) = (int)sVar3 << 2;
              }
              for (uVar16 = 0; uVar16 < *puVar13; uVar16 = uVar16 + 1) {
                sVar3 = FT_Stream_GetUShort(piVar11);
                *(int *)(local_4c + uVar16 * 4) = (int)sVar3 << 2;
              }
            }
            iVar4 = ft_var_apply_tuple(puVar13,uVar7 & 0xffff,local_44,local_48,local_4c);
            if (iVar4 == 0) {
              uVar15 = local_34 + uVar15;
            }
            else {
              local_30 = piVar11[8] - *piVar11;
              if (uVar15 < (uint)(piVar11[9] - *piVar11)) {
                iVar14 = *piVar11 + uVar15;
              }
              else {
                iVar14 = piVar11[9];
              }
              piVar11[8] = iVar14;
              if ((int)(uVar7 << 0x12) < 0) {
                iVar12 = ft_var_readpackedpoints(piVar11,puVar13[0x13],&local_68);
                local_54 = iVar12;
              }
              else {
                local_54 = local_50;
                local_68 = local_40;
              }
              uVar7 = local_68;
              if (local_68 == 0) {
                uVar7 = param_4;
              }
              local_58 = ft_var_readpackeddeltas(piVar11,puVar13[0x13],uVar7);
              uVar7 = local_68;
              if (local_68 == 0) {
                uVar7 = param_4;
              }
              local_5c = ft_var_readpackeddeltas(piVar11,puVar13[0x13],uVar7);
              if (((local_54 != 0) && (local_5c != 0)) && (local_58 != 0)) {
                if (local_54 == -1) {
                  for (uVar7 = 0; uVar7 < param_4; uVar7 = uVar7 + 1) {
                    iVar14 = FT_MulFix((int)*(short *)(local_58 + uVar7 * 2),iVar4);
                    iVar5 = FT_MulFix((int)*(short *)(local_5c + uVar7 * 2),iVar4);
                    if (uVar7 < param_4 - 4) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8) =
                           iVar14 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8);
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4) =
                           iVar5 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4);
                    }
                    else if ((uVar7 == param_4 - 4) &&
                            (-1 < (int)((uint)*(byte *)(local_28 + 0x2c0) << 0x1d))) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8) =
                           iVar14 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8);
                    }
                    else if ((uVar7 == param_4 - 3) &&
                            (-1 < (int)((uint)*(byte *)(local_28 + 0x2c0) << 0x1e))) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8) =
                           iVar14 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8);
                    }
                    else if ((uVar7 == param_4 - 2) &&
                            (-1 < (int)((uint)*(byte *)(local_28 + 0x2c0) << 0x1a))) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4) =
                           iVar5 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4);
                    }
                    else if ((uVar7 == param_4 - 1) &&
                            (-1 < (int)((uint)*(byte *)(local_28 + 0x2c0) << 0x1b))) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4) =
                           iVar5 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4);
                    }
                  }
                }
                else {
                  for (uVar7 = 0; uVar7 < param_4; uVar7 = uVar7 + 1) {
                    *(undefined1 *)(local_60 + uVar7) = 0;
                    puVar8 = (undefined4 *)(local_64 + uVar7 * 8);
                    uVar6 = puVar8[1];
                    puVar9 = (undefined4 *)(iVar10 + uVar7 * 8);
                    *puVar9 = *puVar8;
                    puVar9[1] = uVar6;
                  }
                  for (uVar7 = 0; uVar7 < local_68; uVar7 = uVar7 + 1) {
                    uVar1 = *(ushort *)(local_54 + uVar7 * 2);
                    if (uVar1 < param_4) {
                      *(undefined1 *)(local_60 + (uint)uVar1) = 1;
                      iVar14 = FT_MulFix((int)*(short *)(local_58 + uVar7 * 2),iVar4);
                      *(int *)(iVar10 + (uint)uVar1 * 8) =
                           iVar14 + *(int *)(iVar10 + (uint)uVar1 * 8);
                      iVar14 = FT_MulFix((int)*(short *)(local_5c + uVar7 * 2),iVar4);
                      *(int *)(iVar10 + (uint)uVar1 * 8 + 4) =
                           iVar14 + *(int *)(iVar10 + (uint)uVar1 * 8 + 4);
                    }
                  }
                  tt_interpolate_deltas(param_3,iVar10,local_64,local_60);
                  for (uVar7 = 0; uVar7 < param_4; uVar7 = uVar7 + 1) {
                    iVar14 = *(int *)(iVar10 + uVar7 * 8) - *(int *)(local_64 + uVar7 * 8);
                    iVar4 = *(int *)(iVar10 + uVar7 * 8 + 4) - *(int *)(local_64 + uVar7 * 8 + 4);
                    if (uVar7 < param_4 - 4) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8) =
                           iVar14 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8);
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4) =
                           iVar4 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4);
                    }
                    else if ((uVar7 == param_4 - 4) &&
                            (-1 < (int)((uint)*(byte *)(local_28 + 0x2c0) << 0x1d))) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8) =
                           iVar14 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8);
                    }
                    else if ((uVar7 == param_4 - 3) &&
                            (-1 < (int)((uint)*(byte *)(local_28 + 0x2c0) << 0x1e))) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8) =
                           iVar14 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8);
                    }
                    else if ((uVar7 == param_4 - 2) &&
                            (-1 < (int)((uint)*(byte *)(local_28 + 0x2c0) << 0x1a))) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4) =
                           iVar4 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4);
                    }
                    else if ((uVar7 == param_4 - 1) &&
                            (-1 < (int)((uint)*(byte *)(local_28 + 0x2c0) << 0x1b))) {
                      *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4) =
                           iVar4 + *(int *)(*(int *)(param_3 + 4) + uVar7 * 8 + 4);
                    }
                  }
                }
              }
              if (iVar12 != -1) {
                ft_mem_free(local_6c,iVar12);
                iVar12 = 0;
              }
              ft_mem_free(local_6c,local_58);
              ft_mem_free(local_6c,local_5c);
              uVar15 = local_34 + uVar15;
              if (local_30 < (uint)(piVar11[9] - *piVar11)) {
                iVar4 = *piVar11 + local_30;
              }
              else {
                iVar4 = piVar11[9];
              }
              piVar11[8] = iVar4;
            }
          }
        }
      }
      if (local_50 != -1) {
        ft_mem_free(local_6c,local_50);
      }
      ft_mem_free(local_6c,local_44);
      ft_mem_free(local_6c,local_48);
      ft_mem_free(local_6c,local_4c);
      FT_Stream_ExitFrame(piVar11);
    }
    ft_mem_free(local_6c,local_64);
    ft_mem_free(local_6c,iVar10);
    ft_mem_free(local_6c,local_60);
  }
  else {
    local_70 = 0;
  }
  return local_70;
}

