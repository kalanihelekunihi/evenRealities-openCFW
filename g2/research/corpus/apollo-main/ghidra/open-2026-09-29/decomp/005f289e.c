
int TT_Get_MM_Var(int param_1,int *param_2)

{
  undefined4 uVar1;
  uint *puVar2;
  uint uVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined2 *puVar8;
  int iVar9;
  int *piVar10;
  undefined4 *puVar11;
  int iVar12;
  uint uVar13;
  undefined4 *puVar14;
  bool bVar15;
  int local_80;
  int *local_7c;
  char local_78;
  int local_74;
  int local_70;
  uint local_6c;
  int local_68;
  undefined4 local_64;
  int local_60;
  uint local_5c;
  int local_58;
  undefined1 auStack_54 [4];
  undefined1 auStack_50 [4];
  ushort local_4c;
  ushort local_4a;
  ushort local_46;
  ushort local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  undefined2 local_30;
  ushort local_2e;
  int iStack_2c;
  int *local_28;
  
  local_70 = *(int *)(param_1 + 0x68);
  local_64 = *(undefined4 *)(param_1 + 100);
  local_74 = 0;
  iVar9 = 0;
  local_78 = '\0';
  bVar15 = *(int *)(param_1 + 700) != 0;
  iStack_2c = param_1;
  local_28 = param_2;
  if (bVar15) {
    uVar6 = **(uint **)(param_1 + 700);
  }
  else {
    local_74 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f2fdc,local_70,auStack_54);
    if ((local_74 != 0) &&
       (local_74 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f3234,local_70,auStack_54),
       local_74 != 0)) {
      return local_74;
    }
    local_74 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f3238,local_70,auStack_54);
    if (local_74 != 0) {
      return local_74;
    }
    iVar9 = *(int *)(local_70 + 8);
    local_74 = FT_Stream_ReadFields(local_70,DAT_005f323c,auStack_50);
    if (local_74 != 0) {
      return local_74;
    }
    local_78 = (uint)local_44 == (uint)local_4a * 4 + 6;
    uVar1 = ft_mem_alloc(local_64,0x50,&local_74);
    *(undefined4 *)(param_1 + 700) = uVar1;
    if (local_74 != 0) {
      return local_74;
    }
    uVar6 = (uint)local_4a;
    **(uint **)(param_1 + 700) = uVar6;
  }
  local_6c = *(uint *)(param_1 + 0xc) >> 0x10;
  local_58 = 0x14;
  local_5c = uVar6 * 2 + 3 & 0xfffffffc;
  local_60 = uVar6 * 0x18;
  local_68 = local_6c * 0xc;
  iVar7 = uVar6 * local_6c * 4;
  if (!bVar15) {
    *(uint *)(*(int *)(param_1 + 700) + 0x10) = iVar7 + local_68 + uVar6 * 0x1d + local_5c + 0x14;
    puVar2 = (uint *)ft_mem_alloc(local_64,*(undefined4 *)(*(int *)(param_1 + 700) + 0x10),&local_74
                                 );
    if (local_74 != 0) {
      return local_74;
    }
    *(uint **)(*(int *)(param_1 + 700) + 0xc) = puVar2;
    *puVar2 = uVar6;
    puVar2[1] = 0xffffffff;
    puVar2[2] = local_6c;
    puVar8 = (undefined2 *)((int)puVar2 + local_58);
    puVar2[3] = local_5c + (int)puVar8;
    puVar2[4] = puVar2[3] + local_60;
    iVar5 = local_68 + puVar2[4];
    for (uVar3 = 0; uVar3 < local_6c; uVar3 = uVar3 + 1) {
      *(int *)(puVar2[4] + uVar3 * 0xc) = iVar5;
      iVar5 = iVar5 + uVar6 * 4;
    }
    iVar5 = puVar2[4] + local_68 + iVar7;
    for (uVar3 = 0; uVar3 < uVar6; uVar3 = uVar3 + 1) {
      *(int *)(puVar2[3] + uVar3 * 0x18) = iVar5;
      iVar5 = iVar5 + 5;
    }
    iVar9 = FT_Stream_Seek(local_70,iVar9 + (uint)local_4c);
    if (iVar9 != 0) {
      return iVar9;
    }
    piVar10 = (int *)puVar2[3];
    for (uVar3 = 0; local_74 = 0, uVar3 < uVar6; uVar3 = uVar3 + 1) {
      iVar9 = FT_Stream_ReadFields(local_70,DAT_005f3718,&local_40);
      if (iVar9 != 0) {
        return iVar9;
      }
      piVar10[4] = local_40;
      piVar10[1] = local_3c;
      piVar10[2] = local_38;
      piVar10[3] = local_34;
      piVar10[5] = (uint)local_2e;
      *(char *)*piVar10 = (char)((uint)piVar10[4] >> 0x18);
      *(char *)(*piVar10 + 1) = (char)((uint)piVar10[4] >> 0x10);
      *(char *)(*piVar10 + 2) = (char)((uint)piVar10[4] >> 8);
      *(char *)(*piVar10 + 3) = (char)piVar10[4];
      *(undefined1 *)(*piVar10 + 4) = 0;
      *puVar8 = local_30;
      if ((piVar10[2] < piVar10[1]) || (piVar10[3] < piVar10[2])) {
        piVar10[1] = piVar10[2];
        piVar10[3] = piVar10[2];
      }
      piVar10 = piVar10 + 6;
      puVar8 = puVar8 + 1;
    }
    local_7c = &local_74;
    local_80 = 0;
    uVar1 = ft_mem_realloc(local_64,4,0,local_6c * uVar6);
    *(undefined4 *)(*(int *)(param_1 + 700) + 0x14) = uVar1;
    if (local_74 != 0) {
      return local_74;
    }
    if ((local_46 != 0) && (*(char *)(*(int *)(param_1 + 700) + 0x18) == '\0')) {
      uVar1 = *(undefined4 *)(local_70 + 8);
      ft_var_load_avar(param_1);
      local_74 = FT_Stream_Seek(local_70,uVar1);
      if (local_74 != 0) {
        return local_74;
      }
    }
    puVar11 = (undefined4 *)puVar2[4];
    local_80 = *(int *)(*(int *)(param_1 + 700) + 0x14);
    for (uVar3 = 0; uVar3 < local_46; uVar3 = uVar3 + 1) {
      if (local_78 == '\0') {
        iVar9 = 4;
      }
      else {
        iVar9 = 6;
      }
      local_74 = FT_Stream_EnterFrame(local_70,iVar9 + uVar6 * 4);
      if (local_74 != 0) {
        return local_74;
      }
      uVar1 = FT_Stream_GetUShort(local_70);
      puVar11[1] = uVar1;
      FT_Stream_GetUShort(local_70);
      puVar14 = (undefined4 *)*puVar11;
      for (uVar13 = 0; uVar13 < uVar6; uVar13 = uVar13 + 1) {
        uVar1 = FT_Stream_GetULong(local_70);
        *puVar14 = uVar1;
        puVar14 = puVar14 + 1;
      }
      if (local_78 == '\0') {
        puVar11[2] = 0xffff;
      }
      else {
        uVar1 = FT_Stream_GetUShort(local_70);
        puVar11[2] = uVar1;
      }
      ft_var_to_normalized(param_1,uVar6,*puVar11,local_80);
      local_80 = local_80 + uVar6 * 4;
      FT_Stream_ExitFrame(local_70);
      puVar11 = puVar11 + 3;
    }
    if (local_6c != local_46) {
      iVar12 = *(int *)(param_1 + 0x21c);
      iVar5 = -1;
      iVar9 = (**(code **)(iVar12 + 0x78))(param_1,0x11,&local_7c,&local_80);
      if (iVar9 == 0) {
        iVar9 = (**(code **)(iVar12 + 0x78))(param_1,2,&local_7c,&local_80);
        if (iVar9 != 0) {
          iVar5 = 2;
        }
      }
      else {
        iVar5 = 0x11;
      }
      if ((iVar9 != 0) &&
         (iVar9 = (**(code **)(iVar12 + 0x78))(param_1,6,&local_7c,&local_80), iVar9 != 0)) {
        piVar10 = (int *)(puVar2[4] + (uint)local_46 * 0xc);
        piVar10[1] = iVar5;
        piVar10[2] = 6;
        uVar13 = puVar2[3];
        puVar11 = (undefined4 *)*piVar10;
        for (uVar3 = 0; uVar3 < uVar6; uVar3 = uVar3 + 1) {
          *puVar11 = *(undefined4 *)(uVar13 + 8);
          uVar13 = uVar13 + 0x18;
          puVar11 = puVar11 + 1;
        }
      }
    }
    ft_var_load_mvar(param_1);
  }
  piVar10 = local_28;
  if ((local_28 != (int *)0x0) &&
     (iVar9 = ft_mem_alloc(local_64,*(undefined4 *)(*(int *)(param_1 + 700) + 0x10),&local_74),
     local_74 == 0)) {
    FUN_00439be4(iVar9,*(undefined4 *)(*(int *)(param_1 + 700) + 0xc),
                 *(undefined4 *)(*(int *)(param_1 + 700) + 0x10));
    *(uint *)(iVar9 + 0xc) = local_58 + iVar9 + local_5c;
    *(int *)(iVar9 + 0x10) = *(int *)(iVar9 + 0xc) + local_60;
    iVar5 = *(int *)(iVar9 + 0x10) + local_68;
    for (uVar3 = 0; uVar3 < *(uint *)(iVar9 + 8); uVar3 = uVar3 + 1) {
      *(int *)(*(int *)(iVar9 + 0x10) + uVar3 * 0xc) = iVar5;
      iVar5 = iVar5 + uVar6 * 4;
    }
    piVar4 = *(int **)(iVar9 + 0xc);
    iVar7 = *(int *)(iVar9 + 0x10) + local_68 + iVar7;
    for (uVar3 = 0; uVar3 < uVar6; uVar3 = uVar3 + 1) {
      *piVar4 = iVar7;
      if (piVar4[4] == DAT_005f372c) {
        *piVar4 = DAT_005f3730;
      }
      else if (piVar4[4] == DAT_005f3734) {
        *piVar4 = DAT_005f3738;
      }
      else if (piVar4[4] == DAT_005f3724) {
        *piVar4 = DAT_005f3728;
      }
      else if (piVar4[4] == DAT_005f371c) {
        *piVar4 = DAT_005f3720;
      }
      iVar7 = iVar7 + 5;
      piVar4 = piVar4 + 6;
    }
    *piVar10 = iVar9;
  }
  return local_74;
}

