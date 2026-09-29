
int cff_vstore_load(uint *param_1,int param_2,int param_3,int param_4)

{
  bool bVar1;
  undefined2 uVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  ushort uVar6;
  int iVar7;
  uint uVar8;
  undefined4 uVar9;
  uint uVar10;
  uint *puVar11;
  int *piVar12;
  int unaff_r10;
  int unaff_r11;
  int local_38;
  undefined4 local_34;
  int local_30;
  int *local_2c;
  int local_28;
  
  local_34 = *(undefined4 *)(param_2 + 0x1c);
  local_38 = 3;
  local_30 = 0;
  if (param_4 != 0) {
    local_38 = FT_Stream_Seek(param_2,param_4 + param_3);
    if ((local_38 != 0) || (local_38 = FT_Stream_Skip(param_2,2), local_38 != 0)) goto LAB_005ae40c;
    local_28 = *(int *)(param_2 + 8);
    iVar7 = FT_Stream_ReadUShort(param_2,&local_38);
    if (local_38 != 0) goto LAB_005ae40c;
    if (iVar7 != 1) {
      local_38 = 3;
      goto LAB_005ae40c;
    }
    iVar7 = FT_Stream_ReadULong(param_2,&local_38);
    if (local_38 == 0) {
      uVar8 = FT_Stream_ReadUShort(param_2,&local_38);
      *param_1 = uVar8;
      if (local_38 != 0) goto LAB_005ae200;
      bVar1 = false;
    }
    else {
LAB_005ae200:
      bVar1 = true;
    }
    if ((bVar1) || (local_30 = ft_mem_realloc(local_34,4,0,*param_1,0,&local_38), local_38 != 0))
    goto LAB_005ae40c;
    for (uVar8 = 0; uVar8 < *param_1; uVar8 = uVar8 + 1) {
      uVar9 = FT_Stream_ReadULong(param_2,&local_38);
      *(undefined4 *)(local_30 + uVar8 * 4) = uVar9;
      if (local_38 != 0) goto LAB_005ae40c;
    }
    local_38 = FT_Stream_Seek(param_2,iVar7 + local_28);
    if (local_38 != 0) goto LAB_005ae40c;
    uVar2 = FT_Stream_ReadUShort(param_2,&local_38);
    *(undefined2 *)(param_1 + 2) = uVar2;
    if (local_38 != 0) goto LAB_005ae40c;
    uVar8 = FT_Stream_ReadUShort(param_2,&local_38);
    param_1[3] = uVar8;
    if (local_38 != 0) goto LAB_005ae40c;
    uVar8 = ft_mem_realloc(local_34,4,0,param_1[3],0,&local_38);
    param_1[4] = uVar8;
    if (local_38 != 0) goto LAB_005ae40c;
    for (uVar8 = 0; uVar8 < param_1[3]; uVar8 = uVar8 + 1) {
      local_2c = (int *)(param_1[4] + uVar8 * 4);
      iVar7 = ft_mem_realloc(local_34,0xc,0,(short)param_1[2],0,&local_38);
      *local_2c = iVar7;
      if (local_38 != 0) goto LAB_005ae40c;
      uVar10 = 0;
      while( true ) {
        sVar5 = (short)unaff_r11;
        sVar4 = (short)unaff_r10;
        if ((ushort)param_1[2] <= uVar10) break;
        piVar12 = (int *)(*local_2c + uVar10 * 0xc);
        sVar3 = FT_Stream_ReadUShort(param_2,&local_38);
        if (((local_38 == 0) && (sVar4 = FT_Stream_ReadUShort(param_2,&local_38), local_38 == 0)) &&
           (sVar5 = FT_Stream_ReadUShort(param_2,&local_38), local_38 == 0)) {
          bVar1 = false;
        }
        else {
          bVar1 = true;
        }
        if (bVar1) goto LAB_005ae40c;
        *piVar12 = (int)sVar3 << 2;
        unaff_r10 = (int)sVar4 << 2;
        piVar12[1] = unaff_r10;
        unaff_r11 = (int)sVar5 << 2;
        piVar12[2] = unaff_r11;
        uVar10 = uVar10 + 1;
      }
    }
    uVar8 = ft_mem_realloc(local_34,8,0,*param_1,0,&local_38);
    param_1[1] = uVar8;
    if (local_38 != 0) goto LAB_005ae40c;
    for (uVar8 = 0; uVar8 < *param_1; uVar8 = uVar8 + 1) {
      puVar11 = (uint *)(param_1[1] + uVar8 * 8);
      local_38 = FT_Stream_Seek(param_2,*(int *)(local_30 + uVar8 * 4) + local_28);
      if ((local_38 != 0) || (local_38 = FT_Stream_Skip(param_2,4), local_38 != 0))
      goto LAB_005ae40c;
      uVar10 = FT_Stream_ReadUShort(param_2,&local_38);
      *puVar11 = uVar10;
      if (local_38 != 0) goto LAB_005ae40c;
      uVar10 = ft_mem_realloc(local_34,4,0,*puVar11,0,&local_38);
      puVar11[1] = uVar10;
      if (local_38 != 0) goto LAB_005ae40c;
      for (uVar10 = 0; uVar10 < *puVar11; uVar10 = uVar10 + 1) {
        uVar6 = FT_Stream_ReadUShort(param_2,&local_38);
        *(uint *)(puVar11[1] + uVar10 * 4) = (uint)uVar6;
        if (local_38 != 0) goto LAB_005ae40c;
      }
    }
  }
  local_38 = 0;
LAB_005ae40c:
  ft_mem_free(local_34,local_30);
  if (local_38 != 0) {
    cff_vstore_done(param_1,local_34);
  }
  return local_38;
}

