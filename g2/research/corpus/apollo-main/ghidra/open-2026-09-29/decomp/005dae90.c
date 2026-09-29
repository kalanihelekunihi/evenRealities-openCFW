
int FUN_005dae90(int param_1,int param_2)

{
  bool bVar1;
  undefined1 *puVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  undefined4 *puVar9;
  undefined1 *puVar10;
  uint *puVar11;
  int *local_64;
  int local_60;
  undefined4 local_5c;
  int local_58;
  undefined1 auStack_54 [4];
  int local_50;
  uint local_4c;
  ushort local_48;
  uint local_44;
  uint local_3c;
  int local_38;
  int local_34;
  uint local_30;
  int local_2c;
  int local_28;
  
  local_5c = *(undefined4 *)(param_1 + 0x1c);
  local_60 = 0;
  local_58 = 0;
  iVar7 = 0;
  iVar6 = 0;
  uVar8 = 0;
  local_28 = param_2;
  local_60 = FT_Stream_ReadFields(param_1,DAT_005db938,auStack_54);
  if (local_60 != 0) {
    return local_60;
  }
  if ((local_50 == DAT_005db93c) || (local_50 == DAT_005db940)) {
    return 8;
  }
  if ((((((local_4c != *(uint *)(param_1 + 4)) || (local_48 == 0)) ||
        (local_4c <= (uint)local_48 * 0x14 + 0x2c)) ||
       ((local_44 <= (uint)local_48 * 0x10 + 0xc || ((local_44 & 3) != 0)))) ||
      ((local_3c == 0 && ((local_38 != 0 || (local_34 != 0)))))) ||
     (((local_38 != 0 && (local_34 == 0)) || ((local_30 == 0 && (local_2c != 0)))))) {
    return 8;
  }
  puVar2 = (undefined1 *)ft_mem_alloc(local_5c,(uint)local_48 * 0x10 + 0xc,&local_60);
  if ((local_60 == 0) && (iVar6 = ft_mem_alloc(local_5c,0x28,&local_60), local_60 == 0)) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  if (bVar1) goto LAB_005db3a2;
  iVar5 = 0;
  for (uVar3 = (uint)local_48; uVar3 != 0; uVar3 = uVar3 >> 1) {
    iVar5 = iVar5 + 1;
  }
  uVar3 = iVar5 - 1;
  iVar5 = 1 << (uVar3 & 0xff);
  iVar4 = iVar5 * 0x10;
  iVar5 = (uint)local_48 * 0x10 + iVar5 * -0x10;
  *puVar2 = (char)((uint)local_50 >> 0x18);
  puVar2[1] = (char)((uint)local_50 >> 0x10);
  puVar2[2] = (char)((uint)local_50 >> 8);
  puVar2[3] = (char)local_50;
  puVar2[4] = (char)(local_48 >> 8);
  puVar2[5] = (char)local_48;
  puVar2[6] = (char)((uint)iVar4 >> 8);
  puVar2[7] = (char)iVar4;
  puVar2[8] = (char)(uVar3 >> 8);
  puVar2[9] = (char)uVar3;
  puVar2[10] = (char)((uint)iVar5 >> 8);
  puVar2[0xb] = (char)iVar5;
  local_64 = &local_60;
  local_58 = ft_mem_realloc(local_5c,0x18,0,local_48,0);
  if (local_60 == 0) {
    local_64 = &local_60;
    iVar7 = ft_mem_realloc(local_5c,4,0,local_48,0);
    if (local_60 != 0) goto LAB_005db054;
    bVar1 = false;
  }
  else {
LAB_005db054:
    bVar1 = true;
  }
  if ((!bVar1) && (local_60 = FT_Stream_EnterFrame(param_1,(uint)local_48 * 0x14), local_60 == 0)) {
    for (iVar5 = 0; iVar5 < (int)(uint)local_48; iVar5 = iVar5 + 1) {
      puVar11 = (uint *)(local_58 + iVar5 * 0x18);
      uVar3 = FT_Stream_GetULong(param_1);
      *puVar11 = uVar3;
      uVar3 = FT_Stream_GetULong(param_1);
      puVar11[1] = uVar3;
      uVar3 = FT_Stream_GetULong(param_1);
      puVar11[2] = uVar3;
      uVar3 = FT_Stream_GetULong(param_1);
      puVar11[3] = uVar3;
      uVar3 = FT_Stream_GetULong(param_1);
      puVar11[4] = uVar3;
      if (*puVar11 <= uVar8) {
        FT_Stream_ExitFrame(param_1);
        local_60 = 8;
        goto LAB_005db3a2;
      }
      uVar8 = *puVar11;
      *(uint **)(iVar7 + iVar5 * 4) = puVar11;
    }
    FT_Stream_ExitFrame(param_1);
    FUN_00567c4c(iVar7,local_48,4,DAT_005db944);
    uVar3 = (uint)local_48 * 0x14 + 0x2c;
    uVar8 = (uint)local_48 * 0x10 + 0xc;
    for (iVar5 = 0; iVar5 < (int)(uint)local_48; iVar5 = iVar5 + 1) {
      iVar4 = *(int *)(iVar7 + iVar5 * 4);
      if ((((*(uint *)(iVar4 + 4) != uVar3) || (local_4c < *(uint *)(iVar4 + 8))) ||
          (local_4c - *(int *)(iVar4 + 8) < *(uint *)(iVar4 + 4))) ||
         (((local_44 < *(uint *)(iVar4 + 0xc) || (local_44 - *(int *)(iVar4 + 0xc) < uVar8)) ||
          (*(uint *)(iVar4 + 0xc) < *(uint *)(iVar4 + 8))))) {
        local_60 = 8;
        goto LAB_005db3a2;
      }
      *(uint *)(iVar4 + 0x14) = uVar8;
      uVar3 = (*(int *)(iVar4 + 8) + 3U & 0xfffffffc) + uVar3;
      uVar8 = (*(int *)(iVar4 + 0xc) + 3U & 0xfffffffc) + uVar8;
    }
    if (local_3c != 0) {
      if ((local_3c != uVar3) || (local_4c < local_38 + local_3c)) {
        local_60 = 8;
        goto LAB_005db3a2;
      }
      uVar3 = local_38 + uVar3;
    }
    if (local_30 != 0) {
      uVar3 = uVar3 + 3 & 0xfffffffc;
      if ((local_30 != uVar3) || (local_4c < local_2c + local_30)) {
        local_60 = 8;
        goto LAB_005db3a2;
      }
      uVar3 = local_2c + uVar3;
    }
    if ((uVar8 == local_44) && (uVar3 == local_4c)) {
      local_64 = &local_60;
      puVar2 = (undefined1 *)ft_mem_realloc(local_5c,1,(uint)local_48 * 0x10 + 0xc,local_44,puVar2);
      if (local_60 == 0) {
        puVar10 = puVar2 + 0xc;
        for (iVar5 = 0; iVar4 = local_28, iVar5 < (int)(uint)local_48; iVar5 = iVar5 + 1) {
          puVar9 = (undefined4 *)(local_58 + iVar5 * 0x18);
          *puVar10 = (char)((uint)*puVar9 >> 0x18);
          puVar10[1] = (char)((uint)*puVar9 >> 0x10);
          puVar10[2] = (char)((uint)*puVar9 >> 8);
          puVar10[3] = (char)*puVar9;
          puVar10[4] = (char)((uint)puVar9[4] >> 0x18);
          puVar10[5] = (char)((uint)puVar9[4] >> 0x10);
          puVar10[6] = (char)((uint)puVar9[4] >> 8);
          puVar10[7] = (char)puVar9[4];
          puVar10[8] = (char)((uint)puVar9[5] >> 0x18);
          puVar10[9] = (char)((uint)puVar9[5] >> 0x10);
          puVar10[10] = (char)((uint)puVar9[5] >> 8);
          puVar10[0xb] = (char)puVar9[5];
          puVar10[0xc] = (char)((uint)puVar9[3] >> 0x18);
          puVar10[0xd] = (char)((uint)puVar9[3] >> 0x10);
          puVar10[0xe] = (char)((uint)puVar9[3] >> 8);
          puVar10[0xf] = (char)puVar9[3];
          puVar10 = puVar10 + 0x10;
          local_60 = FT_Stream_Seek(param_1,puVar9[1]);
          if ((local_60 != 0) || (local_60 = FT_Stream_EnterFrame(param_1,puVar9[2]), local_60 != 0)
             ) goto LAB_005db3a2;
          if (puVar9[2] == puVar9[3]) {
            FUN_00439be4(puVar2 + puVar9[5],*(undefined4 *)(param_1 + 0x20),puVar9[3]);
          }
          else {
            local_64 = (int *)puVar9[3];
            local_60 = FUN_005bf004(local_5c,puVar2 + puVar9[5],&local_64,
                                    *(undefined4 *)(param_1 + 0x20),puVar9[2]);
            if (local_60 != 0) goto LAB_005db3a2;
            if (local_64 != (int *)puVar9[3]) {
              local_60 = 8;
              goto LAB_005db3a2;
            }
          }
          FT_Stream_ExitFrame(param_1);
          for (uVar8 = puVar9[3] + puVar9[5]; (uVar8 & 3) != 0; uVar8 = uVar8 + 1) {
            puVar2[uVar8] = 0;
          }
        }
        FT_Stream_OpenMemory(iVar6,puVar2,local_44);
        *(undefined4 *)(iVar6 + 0x1c) = *(undefined4 *)(param_1 + 0x1c);
        *(undefined4 *)(iVar6 + 0x18) = DAT_005db948;
        FT_Stream_Free(*(undefined4 *)(iVar4 + 0x68),*(int *)(iVar4 + 8) >> 10 & 1);
        *(int *)(iVar4 + 0x68) = iVar6;
        *(uint *)(iVar4 + 8) = *(uint *)(iVar4 + 8) & 0xfffffbff;
      }
    }
    else {
      local_60 = 8;
    }
  }
LAB_005db3a2:
  ft_mem_free(local_5c,local_58);
  ft_mem_free(local_5c,iVar7);
  if (local_60 != 0) {
    ft_mem_free(local_5c,puVar2);
    FT_Stream_Close(iVar6);
    ft_mem_free(local_5c,iVar6);
  }
  return local_60;
}

