
undefined8
FT_Raccess_Get_DataOffsets
          (undefined4 *param_1,int param_2,int param_3,int param_4,int param_5,char param_6,
          int *param_7,int *param_8)

{
  bool bVar1;
  short sVar2;
  undefined2 uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  int unaff_r9;
  int unaff_r10;
  int local_28;
  
  uVar8 = *param_1;
  iVar7 = param_2;
  local_28 = param_4;
  local_28 = FT_Stream_Seek(param_2,param_3);
  if (local_28 == 0) {
    sVar2 = FT_Stream_ReadUShort(param_2,&local_28);
    if (local_28 == 0) {
      iVar7 = sVar2 + 1;
      if (iVar7 < 0xff0) {
        for (iVar9 = 0; iVar9 < iVar7; iVar9 = iVar9 + 1) {
          iVar4 = FT_Stream_ReadULong(param_2,&local_28);
          if (local_28 == 0) {
            sVar2 = FT_Stream_ReadUShort(param_2,&local_28);
            unaff_r9 = (int)sVar2;
            if (local_28 != 0) goto LAB_0052832e;
            sVar2 = FT_Stream_ReadUShort(param_2,&local_28);
            unaff_r10 = (int)sVar2;
            if (local_28 != 0) goto LAB_0052832e;
            bVar1 = false;
          }
          else {
LAB_0052832e:
            bVar1 = true;
          }
          if (bVar1) goto LAB_0052846c;
          if (iVar4 == param_5) {
            *param_8 = unaff_r9 + 1;
            if (0xaa6 < *param_8 - 1U) {
              local_28 = 8;
              goto LAB_0052846c;
            }
            local_28 = FT_Stream_Seek(param_2,param_3 + unaff_r10);
            if (local_28 != 0) goto LAB_0052846c;
            iVar7 = 0;
            iVar9 = ft_mem_realloc(uVar8,8,0,*param_8,0,&local_28);
            if (local_28 != 0) goto LAB_0052846c;
            iVar4 = 0;
            goto LAB_005283a6;
          }
        }
        local_28 = 1;
      }
      else {
        local_28 = 8;
      }
    }
  }
  goto LAB_0052846c;
LAB_005283a6:
  if (*param_8 <= iVar4) goto LAB_005283fe;
  uVar3 = FT_Stream_ReadUShort(param_2,&local_28);
  *(undefined2 *)(iVar9 + iVar4 * 8) = uVar3;
  if ((((local_28 != 0) || (local_28 = FT_Stream_Skip(param_2,2), local_28 != 0)) ||
      (uVar5 = FT_Stream_ReadULong(param_2,&local_28), local_28 != 0)) ||
     (local_28 = FT_Stream_Skip(param_2,4), local_28 != 0)) goto LAB_0052845c;
  if ((int)uVar5 < 0) {
    local_28 = 8;
    goto LAB_0052845c;
  }
  *(uint *)(iVar9 + iVar4 * 8 + 4) = uVar5 & 0xffffff;
  iVar4 = iVar4 + 1;
  goto LAB_005283a6;
LAB_005283fe:
  if (param_6 != '\0') {
    FUN_00567c4c(iVar9,*param_8,8,DAT_00528710);
    for (iVar7 = 0; iVar7 < *param_8; iVar7 = iVar7 + 1) {
    }
  }
  iVar7 = 0;
  iVar4 = ft_mem_realloc(uVar8,4,0,*param_8,0,&local_28);
  if (local_28 == 0) {
    for (iVar6 = 0; iVar6 < *param_8; iVar6 = iVar6 + 1) {
      *(int *)(iVar4 + iVar6 * 4) = *(int *)(iVar9 + iVar6 * 8 + 4) + param_4;
    }
    *param_7 = iVar4;
    local_28 = 0;
  }
LAB_0052845c:
  ft_mem_free(uVar8,iVar9);
LAB_0052846c:
  return CONCAT44(iVar7,local_28);
}

