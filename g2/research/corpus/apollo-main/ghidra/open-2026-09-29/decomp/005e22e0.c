
int FUN_005e22e0(int param_1,int param_2,uint param_3,int *param_4,uint param_5)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint *puVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  bool bVar11;
  bool bVar12;
  int local_68;
  int local_64;
  undefined4 local_60;
  uint local_5c;
  uint *local_58;
  int local_54;
  undefined4 local_50;
  uint local_28;
  
  local_68 = 0;
  local_64 = param_2 + 0x6c;
  puVar7 = (uint *)(param_2 + 0x4c);
  local_60 = *(undefined4 *)(param_1 + 8);
  iVar8 = 0;
  iVar10 = 0;
  local_28._0_1_ = (char)param_3;
  bVar11 = (char)local_28 == '\x03';
  bVar12 = (char)local_28 == '\x04';
  local_28 = param_3;
  if (*(int *)(param_2 + 0x48) == *(int *)(param_1 + 0x10)) {
    if ((param_3 & 0xff) == (param_5 & 0xff)) {
      if ((int)((uint)*(byte *)(*(int *)(param_2 + 0x9c) + 4) << 0x1f) < 0) {
        ft_mem_free(local_60,*(undefined4 *)(param_2 + 0x58));
        *(undefined4 *)(param_2 + 0x58) = 0;
        *(uint *)(*(int *)(param_2 + 0x9c) + 4) =
             *(uint *)(*(int *)(param_2 + 0x9c) + 4) & 0xfffffffe;
      }
      ft_glyphslot_preset_bitmap(param_2,local_28 & 0xff,param_4);
      uVar1 = ft_mem_realloc(local_60,*(undefined4 *)(param_2 + 0x54),0,*puVar7,0,&local_68);
      *(undefined4 *)(param_2 + 0x58) = uVar1;
      if (local_68 == 0) {
        *(uint *)(*(int *)(param_2 + 0x9c) + 4) = *(uint *)(*(int *)(param_2 + 0x9c) + 4) | 1;
        iVar9 = *(int *)(param_2 + 100) * -0x40;
        if (*(char *)(param_2 + 0x5e) == '\x06') {
          iVar2 = (int)(*puVar7 << 6) / 3;
        }
        else {
          iVar2 = *puVar7 << 6;
        }
        iVar2 = iVar2 + *(int *)(param_2 + 0x68) * -0x40;
        if (param_4 != (int *)0x0) {
          iVar9 = *param_4 + iVar9;
          iVar2 = param_4[1] + iVar2;
        }
        if (iVar2 != 0 || iVar9 != 0) {
          FT_Outline_Translate(local_64,iVar9,iVar2);
        }
        local_54 = local_64;
        local_50 = 1;
        iVar8 = iVar9;
        iVar10 = iVar2;
        local_58 = puVar7;
        if (bVar11) {
          local_5c = *puVar7;
          iVar2 = *(int *)(param_2 + 0x54);
          uVar4 = *(uint *)(param_2 + 0x50) / 3;
          *(uint *)(param_2 + 0x58) = *(int *)(param_2 + 0x58) + uVar4;
          local_68 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x34),&local_58);
          if (local_68 == 0) {
            FT_Outline_Translate(local_64,0xffffffeb,0);
            *(uint *)(param_2 + 0x58) = *(int *)(param_2 + 0x58) + uVar4;
            local_68 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x34),&local_58);
            iVar8 = iVar9 + -0x15;
            if (local_68 == 0) {
              FT_Outline_Translate(local_64,0x2a,0);
              iVar8 = iVar9 + 0x15;
              *(uint *)(param_2 + 0x58) = *(int *)(param_2 + 0x58) + uVar4 * -2;
              local_68 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x34),&local_58);
              if ((local_68 == 0) && (iVar9 = ft_mem_alloc(local_60,iVar2,&local_68), local_68 == 0)
                 ) {
                for (uVar5 = 0; uVar5 < local_5c; uVar5 = uVar5 + 1) {
                  iVar6 = *(int *)(param_2 + 0x58) + iVar2 * uVar5;
                  for (uVar3 = 0; uVar3 < uVar4; uVar3 = uVar3 + 1) {
                    *(undefined1 *)(iVar9 + uVar3 * 3) = *(undefined1 *)(iVar6 + uVar3);
                    *(undefined1 *)(uVar3 * 3 + iVar9 + 1) = *(undefined1 *)(iVar6 + uVar4 + uVar3);
                    *(undefined1 *)(uVar3 * 3 + iVar9 + 2) =
                         *(undefined1 *)(iVar6 + uVar4 * 2 + uVar3);
                  }
                  FUN_00439be4(iVar6,iVar9,iVar2);
                }
                ft_mem_free(local_60,iVar9);
              }
            }
          }
        }
        else if (bVar12) {
          iVar9 = *(int *)(param_2 + 0x54);
          *(int *)(param_2 + 0x54) = *(int *)(param_2 + 0x54) * 3;
          *puVar7 = *puVar7 / 3;
          *(int *)(param_2 + 0x58) = *(int *)(param_2 + 0x58) + iVar9;
          local_68 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x34),&local_58);
          if (local_68 == 0) {
            FT_Outline_Translate(local_64,0,0x15);
            *(int *)(param_2 + 0x58) = *(int *)(param_2 + 0x58) + iVar9;
            local_68 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x34),&local_58);
            iVar10 = iVar2 + 0x15;
            if (local_68 == 0) {
              FT_Outline_Translate(local_64,0,0xffffffd6);
              *(int *)(param_2 + 0x58) = *(int *)(param_2 + 0x58) + iVar9 * -2;
              local_68 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x34),&local_58);
              iVar10 = iVar2 + -0x15;
              if (local_68 == 0) {
                *(int *)(param_2 + 0x54) = *(int *)(param_2 + 0x54) / 3;
                *puVar7 = *puVar7 * 3;
              }
            }
          }
        }
        else {
          local_68 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x34),&local_58);
        }
      }
    }
    else {
      local_68 = 0x13;
    }
  }
  else {
    local_68 = 6;
  }
  if (local_68 == 0) {
    *(undefined4 *)(param_2 + 0x48) = DAT_005e2644;
  }
  else if ((int)((uint)*(byte *)(*(int *)(param_2 + 0x9c) + 4) << 0x1f) < 0) {
    ft_mem_free(local_60,*(undefined4 *)(param_2 + 0x58));
    *(undefined4 *)(param_2 + 0x58) = 0;
    *(uint *)(*(int *)(param_2 + 0x9c) + 4) = *(uint *)(*(int *)(param_2 + 0x9c) + 4) & 0xfffffffe;
  }
  if (iVar10 != 0 || iVar8 != 0) {
    FT_Outline_Translate(local_64,-iVar8,-iVar10);
  }
  return local_68;
}

