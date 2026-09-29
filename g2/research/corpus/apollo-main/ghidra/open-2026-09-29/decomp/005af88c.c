
uint cff_face_init(undefined4 param_1,undefined4 *param_2,uint param_3,undefined4 param_4,
                  undefined4 *param_5)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  char *pcVar7;
  char *pcVar8;
  int iVar9;
  int *piVar10;
  bool bVar11;
  bool bVar12;
  undefined4 *local_50;
  uint local_4c;
  uint local_48;
  uint local_44;
  char local_40;
  undefined4 local_3c;
  uint local_38;
  undefined4 local_34;
  undefined4 local_30;
  int local_2c;
  undefined4 local_28;
  
  bVar11 = true;
  bVar12 = false;
  local_40 = '\0';
  local_30 = *(undefined4 *)(param_2[0x18] + 4);
  iVar1 = FT_Get_Module_Interface(local_30,PTR_DAT_005b00c8);
  if (iVar1 == 0) {
    local_44 = 0xb;
  }
  else {
    local_2c = ft_module_get_service(param_2[0x18],PTR_s_postscript_cmaps_005b00cc,1);
    local_28 = FT_Get_Module_Interface(local_30,DAT_005b0004);
    iVar2 = FT_Get_Module_Interface(local_30,PTR_s_psaux_005b00d0);
    if (iVar2 == 0) {
      local_44 = 0xb;
    }
    else {
      param_2[0x8b] = iVar2;
      local_3c = param_1;
      uVar3 = ft_module_get_service(param_2[0x18],PTR_s_cff_load_005b00d4,1);
      local_44 = FT_Stream_Seek(local_3c,0);
      if (local_44 == 0) {
        local_50 = param_5;
        local_38 = param_3;
        local_44 = (**(code **)(iVar1 + 4))(local_3c,param_2,param_3,param_4);
        if (local_44 == 0) {
          if (param_2[0x25] != DAT_005b00d8) {
            return 2;
          }
          if ((int)local_38 < 0) {
            return 0;
          }
          local_40 = '\x01';
          local_44 = (*(code *)param_2[0x81])(param_2,DAT_005b00dc,local_3c,0);
          bVar11 = local_44 != 0;
          if (bVar11) {
            local_44 = (**(code **)(iVar1 + 0x20))(param_2,local_3c);
          }
          else {
            local_50 = param_5;
            local_44 = (**(code **)(iVar1 + 8))(local_3c,param_2,local_38,param_4);
          }
          if (local_44 != 0) {
            return local_44;
          }
          local_44 = (*(code *)param_2[0x81])(param_2,DAT_005b00e0,local_3c,0);
          bVar12 = local_44 == 0;
          if (bVar12) {
            *(undefined1 *)(param_2 + 0xae) = 1;
          }
          if ((local_44 & 0xff) == 0x8e) {
            local_44 = (*(code *)param_2[0x81])(param_2,DAT_005b00e4,local_3c,0);
          }
          if (local_44 != 0) {
            return local_44;
          }
        }
        else {
          uVar4 = FT_Stream_Seek(local_3c,0);
          if (uVar4 != 0) {
            return uVar4;
          }
          local_44 = 0;
        }
        local_34 = param_2[0x19];
        iVar1 = ft_mem_alloc(local_34,0xc40,&local_44);
        if (local_44 == 0) {
          param_2[0xa9] = iVar1;
          local_48 = (uint)bVar12;
          local_4c = (uint)bVar11;
          local_50 = param_2;
          local_44 = cff_font_load(local_30,local_3c,local_38,iVar1);
          if (local_44 == 0) {
            if ((int)local_38 < 0) {
              *param_2 = *(undefined4 *)(iVar1 + 0x10);
              local_44 = 0;
            }
            else {
              *(undefined4 *)(iVar1 + 0xc08) = local_28;
              *(int *)(iVar1 + 0xc0c) = local_2c;
              *(undefined4 *)(iVar1 + 0xc10) = uVar3;
              param_2[1] = local_38 & 0xffff;
              param_2[4] = *(undefined4 *)(iVar1 + 0x14);
              if ((*(int *)(iVar1 + 0x5e0) == 0xffff) && (local_2c == 0)) {
                local_44 = 0xb;
              }
              else {
                iVar2 = param_2[0x8a];
                if (((int)(param_2[2] << 0x17) < 0) &&
                   ((param_2[0x89] != 0 && (local_38 >> 0x10 != 0)))) {
                  local_44 = (**(code **)(param_2[0x89] + 0x1c))(param_2);
                  if (local_44 != 0) {
                    return local_44;
                  }
                  if (iVar2 != 0) {
                    (**(code **)(iVar2 + 0x1c))(param_2);
                  }
                }
                if (*(char *)(iVar1 + 0x59c) == '\0') {
                  if (bVar11 == false) {
                    uVar4 = (uint)*(ushort *)(param_2 + 0x11);
                  }
                  else {
                    uVar4 = 1000;
                  }
                  *(uint *)(iVar1 + 0x5a0) = uVar4;
                }
                piVar10 = (int *)(iVar1 + 0x5a4);
                if (*(int *)(iVar1 + 0x598) == 0) {
                  if (*(int *)(iVar1 + 0x594) < 0) {
                    iVar2 = -*(int *)(iVar1 + 0x594);
                  }
                  else {
                    iVar2 = *(int *)(iVar1 + 0x594);
                  }
                }
                else if (*(int *)(iVar1 + 0x598) < 0) {
                  iVar2 = -*(int *)(iVar1 + 0x598);
                }
                else {
                  iVar2 = *(int *)(iVar1 + 0x598);
                }
                if (iVar2 != 0x10000) {
                  uVar3 = FT_DivFix(*(undefined4 *)(iVar1 + 0x5a0),iVar2);
                  *(undefined4 *)(iVar1 + 0x5a0) = uVar3;
                  uVar3 = FT_DivFix(*(undefined4 *)(iVar1 + 0x58c),iVar2);
                  *(undefined4 *)(iVar1 + 0x58c) = uVar3;
                  uVar3 = FT_DivFix(*(undefined4 *)(iVar1 + 0x594),iVar2);
                  *(undefined4 *)(iVar1 + 0x594) = uVar3;
                  uVar3 = FT_DivFix(*(undefined4 *)(iVar1 + 0x590),iVar2);
                  *(undefined4 *)(iVar1 + 0x590) = uVar3;
                  uVar3 = FT_DivFix(*(undefined4 *)(iVar1 + 0x598),iVar2);
                  *(undefined4 *)(iVar1 + 0x598) = uVar3;
                  iVar5 = FT_DivFix(*piVar10,iVar2);
                  *piVar10 = iVar5;
                  uVar3 = FT_DivFix(*(undefined4 *)(iVar1 + 0x5a8),iVar2);
                  *(undefined4 *)(iVar1 + 0x5a8) = uVar3;
                }
                *piVar10 = *piVar10 >> 0x10;
                *(int *)(iVar1 + 0x5a8) = *(int *)(iVar1 + 0x5a8) >> 0x10;
                for (iVar2 = *(int *)(iVar1 + 0x7e8); iVar2 != 0; iVar2 = iVar2 + -1) {
                  iVar5 = *(int *)(iVar1 + iVar2 * 4 + 0x7e8);
                  if (*(char *)(iVar5 + 0x40) == '\0') {
                    FUN_00439c04(iVar5 + 0x30,iVar1 + 0x58c,0x10);
                    uVar3 = *(undefined4 *)(iVar1 + 0x5a8);
                    *(undefined4 *)(iVar5 + 0x48) = *(undefined4 *)(iVar1 + 0x5a4);
                    *(undefined4 *)(iVar5 + 0x4c) = uVar3;
                    *(undefined4 *)(iVar5 + 0x44) = *(undefined4 *)(iVar1 + 0x5a0);
                  }
                  else if (*(char *)(iVar1 + 0x59c) != '\0') {
                    if ((*(uint *)(iVar1 + 0x5a0) < 2) || (*(uint *)(iVar5 + 0x44) < 2)) {
                      uVar3 = 1;
                    }
                    else if (*(uint *)(iVar1 + 0x5a0) < *(uint *)(iVar5 + 0x44)) {
                      uVar3 = *(undefined4 *)(iVar1 + 0x5a0);
                    }
                    else {
                      uVar3 = *(undefined4 *)(iVar5 + 0x44);
                    }
                    FT_Matrix_Multiply_Scaled(iVar1 + 0x58c,iVar5 + 0x30,uVar3);
                    FT_Vector_Transform_Scaled(iVar5 + 0x48,iVar1 + 0x58c,uVar3);
                    uVar3 = FT_MulDiv(*(undefined4 *)(iVar5 + 0x44),*(undefined4 *)(iVar1 + 0x5a0),
                                      uVar3);
                    *(undefined4 *)(iVar5 + 0x44) = uVar3;
                  }
                  piVar10 = (int *)(iVar5 + 0x48);
                  local_50 = (undefined4 *)(iVar5 + 0x44);
                  if (*(int *)(iVar5 + 0x3c) == 0) {
                    if (*(int *)(iVar5 + 0x38) < 0) {
                      iVar9 = -*(int *)(iVar5 + 0x38);
                    }
                    else {
                      iVar9 = *(int *)(iVar5 + 0x38);
                    }
                  }
                  else if (*(int *)(iVar5 + 0x3c) < 0) {
                    iVar9 = -*(int *)(iVar5 + 0x3c);
                  }
                  else {
                    iVar9 = *(int *)(iVar5 + 0x3c);
                  }
                  if (iVar9 != 0x10000) {
                    uVar3 = FT_DivFix(*local_50,iVar9);
                    *local_50 = uVar3;
                    uVar3 = FT_DivFix(*(undefined4 *)(iVar5 + 0x30),iVar9);
                    *(undefined4 *)(iVar5 + 0x30) = uVar3;
                    uVar3 = FT_DivFix(*(undefined4 *)(iVar5 + 0x38),iVar9);
                    *(undefined4 *)(iVar5 + 0x38) = uVar3;
                    uVar3 = FT_DivFix(*(undefined4 *)(iVar5 + 0x34),iVar9);
                    *(undefined4 *)(iVar5 + 0x34) = uVar3;
                    uVar3 = FT_DivFix(*(undefined4 *)(iVar5 + 0x3c),iVar9);
                    *(undefined4 *)(iVar5 + 0x3c) = uVar3;
                    iVar6 = FT_DivFix(*piVar10,iVar9);
                    *piVar10 = iVar6;
                    uVar3 = FT_DivFix(*(undefined4 *)(iVar5 + 0x4c),iVar9);
                    *(undefined4 *)(iVar5 + 0x4c) = uVar3;
                  }
                  *piVar10 = *piVar10 >> 0x10;
                  *(int *)(iVar5 + 0x4c) = *(int *)(iVar5 + 0x4c) >> 0x10;
                }
                if (bVar11 != false) {
                  iVar2 = 0;
                  *param_2 = *(undefined4 *)(iVar1 + 0x10);
                  if (*(int *)(iVar1 + 0x5e0) == 0xffff) {
                    param_2[4] = *(undefined4 *)(iVar1 + 0x4c0);
                  }
                  else {
                    param_2[4] = *(int *)(iVar1 + 0x4ac) + 1;
                  }
                  param_2[0xd] = *(int *)(iVar1 + 0x5b0) >> 0x10;
                  param_2[0xe] = *(int *)(iVar1 + 0x5b4) >> 0x10;
                  param_2[0xf] = *(int *)(iVar1 + 0x5b8) + 0xffff >> 0x10;
                  param_2[0x10] = *(int *)(iVar1 + 0x5bc) + 0xffff >> 0x10;
                  *(short *)(param_2 + 0x11) = (short)*(undefined4 *)(iVar1 + 0x5a0);
                  *(short *)((int)param_2 + 0x46) = (short)param_2[0x10];
                  *(short *)(param_2 + 0x12) = (short)param_2[0xe];
                  *(short *)((int)param_2 + 0x4a) =
                       (short)(((uint)*(ushort *)(param_2 + 0x11) * 0xc) / 10);
                  if ((int)*(short *)((int)param_2 + 0x4a) <
                      (int)*(short *)((int)param_2 + 0x46) - (int)*(short *)(param_2 + 0x12)) {
                    *(short *)((int)param_2 + 0x4a) =
                         *(short *)((int)param_2 + 0x46) - *(short *)(param_2 + 0x12);
                  }
                  *(short *)(param_2 + 0x14) = (short)((uint)*(undefined4 *)(iVar1 + 0x57c) >> 0x10)
                  ;
                  *(short *)((int)param_2 + 0x52) =
                       (short)((uint)*(undefined4 *)(iVar1 + 0x580) >> 0x10);
                  if ((*(int *)(iVar1 + 0x56c) != 0) &&
                     (iVar5 = cff_index_get_sid_string(iVar1,*(undefined4 *)(iVar1 + 0x56c)),
                     iVar5 != 0)) {
                    uVar3 = cff_strcpy(local_34,iVar5);
                    param_2[5] = uVar3;
                  }
                  if (param_2[5] == 0) {
                    uVar3 = cff_index_get_name(iVar1,local_38 & 0xffff);
                    param_2[5] = uVar3;
                    if (param_2[5] != 0) {
                      remove_subset_prefix(param_2[5]);
                    }
                  }
                  if (param_2[5] == 0) {
                    iVar5 = cff_index_get_sid_string(iVar1,*(undefined4 *)(iVar1 + 0x608));
                    if (iVar5 != 0) {
                      uVar3 = cff_strcpy(local_34,iVar5);
                      param_2[5] = uVar3;
                    }
                  }
                  else {
                    pcVar7 = (char *)cff_index_get_sid_string(iVar1,*(undefined4 *)(iVar1 + 0x568));
                    pcVar8 = (char *)param_2[5];
                    if ((pcVar7 != (char *)0x0) && (pcVar8 != (char *)0x0)) {
                      while (*pcVar7 != '\0') {
                        if (*pcVar7 == *pcVar8) {
                          pcVar8 = pcVar8 + 1;
                          pcVar7 = pcVar7 + 1;
                        }
                        else if ((*pcVar7 == ' ') || (*pcVar7 == '-')) {
                          pcVar7 = pcVar7 + 1;
                        }
                        else {
                          if ((*pcVar8 != ' ') && (*pcVar8 != '-')) {
                            if ((*pcVar8 == '\0') && (*pcVar7 != '\0')) {
                              iVar2 = cff_strcpy(local_34,pcVar7);
                              remove_style(param_2[5],iVar2);
                            }
                            break;
                          }
                          pcVar8 = pcVar8 + 1;
                        }
                      }
                    }
                  }
                  if (iVar2 == 0) {
                    uVar3 = cff_strcpy(local_34,PTR_s_Regular_005b00e8);
                    param_2[6] = uVar3;
                  }
                  else {
                    param_2[6] = iVar2;
                  }
                  uVar4 = 0x811;
                  if (local_40 != '\0') {
                    uVar4 = 0x819;
                  }
                  if (*(char *)(iVar1 + 0x574) != '\0') {
                    uVar4 = uVar4 | 4;
                  }
                  param_2[2] = uVar4 | param_2[2];
                  uVar4 = (uint)(*(int *)(iVar1 + 0x578) != 0);
                  iVar2 = cff_index_get_sid_string(iVar1,*(undefined4 *)(iVar1 + 0x570));
                  if ((iVar2 != 0) &&
                     ((iVar5 = FUN_0046cacc(iVar2,PTR_DAT_005b00ec), iVar5 == 0 ||
                      (iVar2 = FUN_0046cacc(iVar2,PTR_s_Black_005b00f0), iVar2 == 0)))) {
                    uVar4 = uVar4 | 2;
                  }
                  if (((-1 < (int)(uVar4 << 0x1e)) && (param_2[6] != 0)) &&
                     ((iVar2 = FUN_0044b610(param_2[6],PTR_DAT_005b00ec,4), iVar2 == 0 ||
                      (iVar2 = FUN_0044b610(param_2[6],PTR_s_Black_005b00f0,5), iVar2 == 0)))) {
                    uVar4 = uVar4 | 2;
                  }
                  param_2[3] = uVar4;
                }
                if (*(int *)(iVar1 + 0x5e0) == 0xffff) {
                  param_2[2] = param_2[2] | 0x200;
                }
                if ((*(int *)(iVar1 + 0x5e0) != 0xffff) && (bVar11 != false)) {
                  param_2[2] = param_2[2] | 0x1000;
                }
                for (uVar4 = 0; uVar4 < (uint)param_2[9]; uVar4 = uVar4 + 1) {
                  iVar2 = *(int *)(param_2[10] + uVar4 * 4);
                  if (((*(short *)(iVar2 + 8) == 3) && (*(short *)(iVar2 + 10) == 1)) ||
                     (*(short *)(iVar2 + 8) == 0)) goto LAB_005affae;
                }
                if ((bVar11 == false) || (*(int *)(iVar1 + 0x5e0) == 0xffff)) {
                  local_48 = 0x10003;
                  local_4c = DAT_005b00f4;
                  iVar2 = param_2[9];
                  local_50 = param_2;
                  local_44 = FT_CMap_New(DAT_005b00f8,0,&local_50,0);
                  if ((local_44 == 0) || ((local_44 & 0xff) == 0xa3)) {
                    local_44 = 0;
                    if ((param_2[0x17] == 0) && (iVar2 != param_2[9])) {
                      param_2[0x17] = *(undefined4 *)(param_2[10] + iVar2 * 4);
                    }
LAB_005affae:
                    if (*(int *)(iVar1 + 0x98) != 0) {
                      if (*(int *)(iVar1 + 0x94) == 0) {
                        local_48 = 7;
                        local_4c = DAT_005b00fc;
                      }
                      else if (*(int *)(iVar1 + 0x94) == 1) {
                        local_48 = 0x10007;
                        local_4c = DAT_005b0104;
                      }
                      else {
                        local_48 = 0x20007;
                        local_4c = DAT_005b0108;
                      }
                      local_50 = param_2;
                      local_44 = FT_CMap_New(DAT_005b0100,0,&local_50,0);
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  return local_44;
}

