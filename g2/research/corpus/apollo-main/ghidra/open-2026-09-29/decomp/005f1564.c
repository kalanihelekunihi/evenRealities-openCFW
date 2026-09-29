
int ft_var_load_item_variation_store(int param_1,int param_2,uint *param_3)

{
  bool bVar1;
  char cVar2;
  short sVar3;
  undefined2 uVar4;
  short sVar5;
  short sVar6;
  ushort uVar7;
  int iVar8;
  uint uVar9;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  uint unaff_r7;
  uint uVar13;
  int *piVar14;
  uint uVar15;
  int unaff_r10;
  int unaff_r11;
  int local_38;
  undefined4 local_34;
  int local_30;
  int iStack_2c;
  int local_28;
  
  iVar11 = *(int *)(param_1 + 0x68);
  local_34 = *(undefined4 *)(iVar11 + 0x1c);
  iVar12 = *(int *)(param_1 + 700);
  local_30 = 0;
  iStack_2c = param_1;
  local_28 = param_2;
  local_38 = FT_Stream_Seek(iVar11,param_2);
  if ((local_38 != 0) || (sVar3 = FT_Stream_ReadUShort(iVar11,&local_38), local_38 != 0))
  goto LAB_005f18f6;
  if (sVar3 != 1) {
    local_38 = 8;
    goto LAB_005f18f6;
  }
  iVar8 = FT_Stream_ReadULong(iVar11,&local_38);
  if (local_38 == 0) {
    uVar9 = FT_Stream_ReadUShort(iVar11,&local_38);
    *param_3 = uVar9;
    if (local_38 != 0) goto LAB_005f15c6;
    bVar1 = false;
  }
  else {
LAB_005f15c6:
    bVar1 = true;
  }
  if (bVar1) goto LAB_005f18f6;
  if (*param_3 == 0) {
    local_38 = 8;
    goto LAB_005f18f6;
  }
  local_30 = ft_mem_realloc(local_34,4,0,*param_3,0,&local_38);
  if (local_38 != 0) goto LAB_005f18f6;
  for (uVar9 = 0; uVar9 < *param_3; uVar9 = uVar9 + 1) {
    uVar10 = FT_Stream_ReadULong(iVar11,&local_38);
    *(undefined4 *)(local_30 + uVar9 * 4) = uVar10;
    if (local_38 != 0) goto LAB_005f18f6;
  }
  local_38 = FT_Stream_Seek(iVar11,iVar8 + local_28);
  if (local_38 != 0) goto LAB_005f18f6;
  uVar4 = FT_Stream_ReadUShort(iVar11,&local_38);
  *(undefined2 *)(param_3 + 2) = uVar4;
  if (local_38 == 0) {
    uVar9 = FT_Stream_ReadUShort(iVar11,&local_38);
    param_3[3] = uVar9;
    if (local_38 != 0) goto LAB_005f165a;
    bVar1 = false;
  }
  else {
LAB_005f165a:
    bVar1 = true;
  }
  if (!bVar1) {
    if ((uint)(ushort)param_3[2] == **(uint **)(iVar12 + 0xc)) {
      uVar9 = ft_mem_realloc(local_34,4,0,param_3[3],0,&local_38);
      param_3[4] = uVar9;
      if (local_38 == 0) {
        for (uVar9 = 0; uVar9 < param_3[3]; uVar9 = uVar9 + 1) {
          uVar10 = ft_mem_realloc(local_34,0xc,0,(short)param_3[2],0,&local_38);
          *(undefined4 *)(param_3[4] + uVar9 * 4) = uVar10;
          if (local_38 != 0) goto LAB_005f18f6;
          iVar12 = *(int *)(param_3[4] + uVar9 * 4);
          uVar13 = 0;
          while( true ) {
            sVar6 = (short)unaff_r11;
            sVar3 = (short)unaff_r10;
            if ((ushort)param_3[2] <= uVar13) break;
            sVar5 = FT_Stream_ReadUShort(iVar11,&local_38);
            if (((local_38 == 0) && (sVar3 = FT_Stream_ReadUShort(iVar11,&local_38), local_38 == 0))
               && (sVar6 = FT_Stream_ReadUShort(iVar11,&local_38), local_38 == 0)) {
              bVar1 = false;
            }
            else {
              bVar1 = true;
            }
            if (bVar1) goto LAB_005f18f6;
            *(int *)(iVar12 + uVar13 * 0xc) = (int)sVar5 << 2;
            unaff_r10 = (int)sVar3 << 2;
            *(int *)(iVar12 + uVar13 * 0xc + 4) = unaff_r10;
            unaff_r11 = (int)sVar6 << 2;
            *(int *)(uVar13 * 0xc + iVar12 + 8) = unaff_r11;
            uVar13 = uVar13 + 1;
          }
        }
        uVar9 = ft_mem_realloc(local_34,0x10,0,*param_3,0,&local_38);
        param_3[1] = uVar9;
        if (local_38 == 0) {
          for (uVar9 = 0; uVar9 < *param_3; uVar9 = uVar9 + 1) {
            piVar14 = (int *)(param_3[1] + uVar9 * 0x10);
            local_38 = FT_Stream_Seek(iVar11,*(int *)(local_30 + uVar9 * 4) + local_28);
            if (local_38 != 0) break;
            iVar12 = FT_Stream_ReadUShort(iVar11,&local_38);
            *piVar14 = iVar12;
            if ((local_38 == 0) &&
               (unaff_r7 = FT_Stream_ReadUShort(iVar11,&local_38), local_38 == 0)) {
              iVar12 = FT_Stream_ReadUShort(iVar11,&local_38);
              piVar14[1] = iVar12;
              if (local_38 != 0) goto LAB_005f17d4;
              bVar1 = false;
            }
            else {
LAB_005f17d4:
              bVar1 = true;
            }
            if (bVar1) break;
            if ((uint)piVar14[1] < unaff_r7) {
              local_38 = 8;
              break;
            }
            if (param_3[3] < (uint)piVar14[1]) {
              local_38 = 8;
              break;
            }
            iVar12 = ft_mem_realloc(local_34,4,0,piVar14[1],0,&local_38);
            piVar14[2] = iVar12;
            if (local_38 != 0) break;
            for (uVar13 = 0; uVar13 < (uint)piVar14[1]; uVar13 = uVar13 + 1) {
              uVar7 = FT_Stream_ReadUShort(iVar11,&local_38);
              *(uint *)(piVar14[2] + uVar13 * 4) = (uint)uVar7;
              if (local_38 != 0) goto LAB_005f18f6;
              if (param_3[3] <= *(uint *)(piVar14[2] + uVar13 * 4)) {
                local_38 = 8;
                goto LAB_005f18f6;
              }
            }
            iVar12 = ft_mem_realloc(local_34,2,0,*piVar14 * piVar14[1],0,&local_38);
            piVar14[3] = iVar12;
            if (local_38 != 0) break;
            uVar13 = 0;
            while (uVar13 < (uint)(piVar14[1] * *piVar14)) {
              for (uVar15 = 0; uVar15 < unaff_r7; uVar15 = uVar15 + 1) {
                uVar4 = FT_Stream_ReadUShort(iVar11,&local_38);
                if (local_38 != 0) goto LAB_005f18f6;
                *(undefined2 *)(piVar14[3] + uVar13 * 2) = uVar4;
                uVar13 = uVar13 + 1;
              }
              for (; uVar15 < (uint)piVar14[1]; uVar15 = uVar15 + 1) {
                cVar2 = FT_Stream_ReadChar(iVar11,&local_38);
                if (local_38 != 0) goto LAB_005f18f6;
                *(short *)(piVar14[3] + uVar13 * 2) = (short)cVar2;
                uVar13 = uVar13 + 1;
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
LAB_005f18f6:
  ft_mem_free(local_34,local_30);
  return local_38;
}

