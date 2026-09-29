
int tt_face_vary_cvt(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint *puVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  int local_60;
  int local_5c;
  uint local_58;
  uint local_54;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  uint local_40;
  uint local_3c;
  uint local_38;
  int local_34;
  uint local_30;
  int local_2c;
  undefined4 uStack_28;
  
  local_5c = param_2[7];
  local_50 = 0;
  local_44 = 0;
  local_48 = 0;
  puVar7 = *(uint **)(param_1 + 700);
  local_40 = 0;
  local_4c = 0;
  iVar10 = 0;
  uStack_28 = param_4;
  if (puVar7 == (uint *)0x0) {
    local_60 = 0;
  }
  else if (*(int *)(param_1 + 0x29c) == 0) {
    local_60 = 0;
  }
  else {
    local_60 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f3744,param_2,&local_54);
    if (local_60 == 0) {
      local_60 = FT_Stream_EnterFrame(param_2,local_54);
      if (local_60 == 0) {
        iVar8 = param_2[8];
        iVar4 = *param_2;
        iVar5 = FT_Stream_GetULong(param_2);
        if (iVar5 == 0x10000) {
          local_50 = ft_mem_realloc(local_5c,4,0,*puVar7,0,&local_60);
          if (((local_60 == 0) &&
              (local_44 = ft_mem_realloc(local_5c,4,0,*puVar7,0,&local_60), local_60 == 0)) &&
             (local_48 = ft_mem_realloc(local_5c,4,0,*puVar7,0,&local_60), local_60 == 0)) {
            bVar1 = false;
          }
          else {
            bVar1 = true;
          }
          if (!bVar1) {
            local_38 = FT_Stream_GetUShort(param_2);
            iVar5 = FT_Stream_GetUShort(param_2);
            if (local_54 < (local_38 & 0xfff) * 4 + iVar5) {
              local_60 = 8;
            }
            else {
              uVar9 = (iVar8 - iVar4) + iVar5;
              if ((int)(local_38 << 0x10) < 0) {
                iVar5 = param_2[8];
                iVar4 = *param_2;
                if (uVar9 < (uint)(param_2[9] - *param_2)) {
                  iVar8 = *param_2 + uVar9;
                }
                else {
                  iVar8 = param_2[9];
                }
                param_2[8] = iVar8;
                local_4c = ft_var_readpackedpoints(param_2,local_54,&local_40);
                uVar9 = param_2[8] - *param_2;
                if ((uint)(iVar5 - iVar4) < (uint)(param_2[9] - *param_2)) {
                  iVar4 = *param_2 + (iVar5 - iVar4);
                }
                else {
                  iVar4 = param_2[9];
                }
                param_2[8] = iVar4;
              }
              for (local_3c = 0; local_3c < (local_38 & 0xfff); local_3c = local_3c + 1) {
                local_34 = FT_Stream_GetUShort(param_2);
                uVar6 = FT_Stream_GetUShort(param_2);
                if ((int)(uVar6 << 0x10) < 0) {
                  for (uVar11 = 0; uVar11 < *puVar7; uVar11 = uVar11 + 1) {
                    sVar2 = FT_Stream_GetUShort(param_2);
                    *(int *)(local_50 + uVar11 * 4) = (int)sVar2 << 2;
                  }
                }
                else {
                  if (puVar7[0xf] <= (uVar6 & 0xfff)) {
                    local_60 = 8;
                    goto LAB_005f36de;
                  }
                  FUN_00439be4(local_50,puVar7[0x10] + *puVar7 * (uVar6 & 0xfff) * 4,*puVar7 << 2);
                }
                if ((int)(uVar6 << 0x11) < 0) {
                  for (uVar11 = 0; uVar11 < *puVar7; uVar11 = uVar11 + 1) {
                    sVar2 = FT_Stream_GetUShort(param_2);
                    *(int *)(local_44 + uVar11 * 4) = (int)sVar2 << 2;
                  }
                  for (uVar11 = 0; uVar11 < *puVar7; uVar11 = uVar11 + 1) {
                    sVar2 = FT_Stream_GetUShort(param_2);
                    *(int *)(local_48 + uVar11 * 4) = (int)sVar2 << 2;
                  }
                }
                iVar4 = ft_var_apply_tuple(puVar7,uVar6 & 0xffff,local_50,local_44,local_48);
                if (iVar4 != 0) {
                  local_30 = param_2[8] - *param_2;
                  if (uVar9 < (uint)(param_2[9] - *param_2)) {
                    iVar5 = *param_2 + uVar9;
                  }
                  else {
                    iVar5 = param_2[9];
                  }
                  param_2[8] = iVar5;
                  if ((int)(uVar6 << 0x12) < 0) {
                    iVar10 = ft_var_readpackedpoints(param_2,local_54,&local_58);
                    iVar5 = iVar10;
                  }
                  else {
                    local_58 = local_40;
                    iVar5 = local_4c;
                  }
                  uVar6 = local_58;
                  if (local_58 == 0) {
                    uVar6 = *(uint *)(param_1 + 0x298);
                  }
                  iVar8 = ft_var_readpackeddeltas(param_2,local_54,uVar6);
                  if (((iVar5 != 0) && (iVar8 != 0)) &&
                     ((iVar10 != -1 || (local_58 == *(uint *)(param_1 + 0x298))))) {
                    if (iVar10 == -1) {
                      for (uVar6 = 0; uVar6 < *(uint *)(param_1 + 0x298); uVar6 = uVar6 + 1) {
                        sVar2 = *(short *)(*(int *)(param_1 + 0x29c) + uVar6 * 2);
                        sVar3 = FT_MulFix((int)*(short *)(iVar8 + uVar6 * 2),iVar4);
                        *(short *)(*(int *)(param_1 + 0x29c) + uVar6 * 2) = sVar3 + sVar2;
                      }
                    }
                    else {
                      for (uVar6 = 0; uVar6 < local_58; uVar6 = uVar6 + 1) {
                        uVar11 = (uint)*(ushort *)(iVar5 + uVar6 * 2);
                        if (uVar11 < *(uint *)(param_1 + 0x298)) {
                          local_2c = (int)*(short *)(*(int *)(param_1 + 0x29c) + uVar11 * 2);
                          sVar2 = FT_MulFix((int)*(short *)(iVar8 + uVar6 * 2),iVar4);
                          *(short *)(*(int *)(param_1 + 0x29c) + uVar11 * 2) =
                               sVar2 + (short)local_2c;
                        }
                      }
                    }
                  }
                  if (iVar10 != -1) {
                    ft_mem_free(local_5c,iVar10);
                    iVar10 = 0;
                  }
                  ft_mem_free(local_5c,iVar8);
                  if (local_30 < (uint)(param_2[9] - *param_2)) {
                    iVar4 = *param_2 + local_30;
                  }
                  else {
                    iVar4 = param_2[9];
                  }
                  param_2[8] = iVar4;
                }
                uVar9 = local_34 + uVar9;
              }
            }
          }
        }
        else {
          local_60 = 0;
        }
        FT_Stream_ExitFrame(param_2);
      }
      else {
        local_60 = 0;
      }
    }
    else {
      local_60 = 0;
    }
  }
LAB_005f36de:
  if (local_4c != -1) {
    ft_mem_free(local_5c,local_4c);
  }
  ft_mem_free(local_5c,local_50);
  ft_mem_free(local_5c,local_44);
  ft_mem_free(local_5c,local_48);
  return local_60;
}

