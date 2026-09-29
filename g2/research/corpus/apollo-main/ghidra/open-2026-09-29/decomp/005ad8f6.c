
int cff_index_load_offsets(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  bool bVar2;
  int iVar3;
  byte *pbVar4;
  uint *puVar5;
  byte *pbVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  int local_20;
  undefined4 uStack_1c;
  
  local_20 = 0;
  iVar8 = *param_1;
  uVar7 = *(undefined4 *)(iVar8 + 0x1c);
  uStack_1c = param_4;
  if ((param_1[3] == 0) || (param_1[7] != 0)) goto LAB_005ad9e4;
  bVar1 = *(byte *)(param_1 + 4);
  iVar9 = (uint)bVar1 * (param_1[3] + 1);
  iVar3 = ft_mem_realloc(uVar7,4,0,param_1[3] + 1,0,&local_20);
  param_1[7] = iVar3;
  if ((local_20 == 0) &&
     ((local_20 = FT_Stream_Seek(iVar8,param_1[2] + param_1[1]), local_20 == 0 &&
      (local_20 = FT_Stream_EnterFrame(iVar8,iVar9), local_20 == 0)))) {
    bVar2 = false;
  }
  else {
    bVar2 = true;
  }
  if (bVar2) goto LAB_005ad9e4;
  puVar5 = (uint *)param_1[7];
  pbVar4 = *(byte **)(iVar8 + 0x20);
  pbVar6 = pbVar4 + iVar9;
  if (bVar1 == 1) {
    for (; pbVar4 < pbVar6; pbVar4 = pbVar4 + 1) {
      *puVar5 = (uint)*pbVar4;
      puVar5 = puVar5 + 1;
    }
  }
  else if (bVar1 == 0) {
LAB_005ad9da:
    for (; pbVar4 < pbVar6; pbVar4 = pbVar4 + 4) {
      *puVar5 = (uint)pbVar4[1] << 0x10 | (uint)*pbVar4 << 0x18 | (uint)pbVar4[2] << 8 |
                (uint)pbVar4[3];
      puVar5 = puVar5 + 1;
    }
  }
  else if (bVar1 == 3) {
    for (; pbVar4 < pbVar6; pbVar4 = pbVar4 + 3) {
      *puVar5 = (uint)pbVar4[1] << 8 | (uint)*pbVar4 << 0x10 | (uint)pbVar4[2];
      puVar5 = puVar5 + 1;
    }
  }
  else {
    if (2 < bVar1) goto LAB_005ad9da;
    for (; pbVar4 < pbVar6; pbVar4 = pbVar4 + 2) {
      *puVar5 = (uint)CONCAT11(*pbVar4,pbVar4[1]);
      puVar5 = puVar5 + 1;
    }
  }
  FT_Stream_ExitFrame(iVar8);
LAB_005ad9e4:
  if (local_20 != 0) {
    ft_mem_free(uVar7,param_1[7]);
    param_1[7] = 0;
  }
  return local_20;
}

