
int ft_var_load_gvar(int param_1)

{
  ushort uVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  uint uVar11;
  int local_38;
  uint local_34;
  int local_30;
  ushort local_2c;
  ushort local_2a;
  int local_28;
  ushort local_24;
  byte local_22;
  int local_20;
  
  iVar7 = *(int *)(param_1 + 0x68);
  uVar9 = *(undefined4 *)(iVar7 + 0x1c);
  iVar8 = *(int *)(param_1 + 700);
  local_38 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f2fdc,iVar7,&local_34);
  if (local_38 == 0) {
    iVar3 = *(int *)(iVar7 + 8);
    local_38 = FT_Stream_ReadFields(iVar7,DAT_005f2fe0,&local_30);
    if (local_38 == 0) {
      if (local_30 == 0x10000) {
        if ((uint)local_2c == (**(uint **)(iVar8 + 0xc) & 0xffff)) {
          if (local_34 >> 1 < (uint)local_2c * (uint)local_2a) {
            local_38 = 8;
          }
          else {
            if ((int)((uint)local_22 << 0x1f) < 0) {
              iVar4 = 4;
            }
            else {
              iVar4 = 2;
            }
            if (local_34 < iVar4 * (uint)local_24) {
              local_38 = 8;
            }
            else {
              *(uint *)(iVar8 + 0x4c) = local_34;
              *(uint *)(iVar8 + 0x3c) = (uint)local_2a;
              *(uint *)(iVar8 + 0x44) = (uint)local_24;
              iVar4 = local_20 + iVar3;
              uVar5 = ft_mem_realloc(uVar9,4,0,*(int *)(iVar8 + 0x44) + 1,0,&local_38);
              *(undefined4 *)(iVar8 + 0x48) = uVar5;
              if (local_38 == 0) {
                if ((int)((uint)local_22 << 0x1f) < 0) {
                  iVar6 = FT_Stream_EnterFrame(iVar7,(*(int *)(iVar8 + 0x44) + 1) * 4);
                  if (iVar6 != 0) {
                    return iVar6;
                  }
                  local_38 = 0;
                  for (uVar11 = 0; uVar11 <= *(uint *)(iVar8 + 0x44); uVar11 = uVar11 + 1) {
                    iVar6 = FT_Stream_GetULong(iVar7);
                    *(int *)(*(int *)(iVar8 + 0x48) + uVar11 * 4) = iVar6 + iVar4;
                  }
                  FT_Stream_ExitFrame(iVar7);
                }
                else {
                  iVar6 = FT_Stream_EnterFrame(iVar7,(*(int *)(iVar8 + 0x44) + 1) * 2);
                  if (iVar6 != 0) {
                    return iVar6;
                  }
                  local_38 = 0;
                  for (uVar11 = 0; uVar11 <= *(uint *)(iVar8 + 0x44); uVar11 = uVar11 + 1) {
                    uVar1 = FT_Stream_GetUShort(iVar7);
                    *(uint *)(*(int *)(iVar8 + 0x48) + uVar11 * 4) = iVar4 + (uint)uVar1 * 2;
                  }
                  FT_Stream_ExitFrame(iVar7);
                }
                if (*(int *)(iVar8 + 0x3c) != 0) {
                  uVar9 = ft_mem_realloc(uVar9,4,0,*(int *)(iVar8 + 0x3c) * (uint)local_2c,0,
                                         &local_38);
                  *(undefined4 *)(iVar8 + 0x40) = uVar9;
                  if (((local_38 == 0) &&
                      (local_38 = FT_Stream_Seek(iVar7,local_28 + iVar3), local_38 == 0)) &&
                     (local_38 = FT_Stream_EnterFrame
                                           (iVar7,(uint)local_2c * *(int *)(iVar8 + 0x3c) * 2),
                     local_38 == 0)) {
                    for (uVar11 = 0; uVar11 < *(uint *)(iVar8 + 0x3c); uVar11 = uVar11 + 1) {
                      for (uVar10 = 0; uVar10 < local_2c; uVar10 = uVar10 + 1) {
                        sVar2 = FT_Stream_GetUShort(iVar7);
                        *(int *)(*(int *)(iVar8 + 0x40) + (local_2c * uVar11 + uVar10) * 4) =
                             (int)sVar2 << 2;
                      }
                    }
                    FT_Stream_ExitFrame(iVar7);
                  }
                }
              }
            }
          }
        }
        else {
          local_38 = 8;
        }
      }
      else {
        local_38 = 8;
      }
    }
  }
  return local_38;
}

