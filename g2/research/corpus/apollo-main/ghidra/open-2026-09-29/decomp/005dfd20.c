
int FUN_005dfd20(int param_1,int param_2,uint param_3)

{
  bool bVar1;
  undefined2 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  ushort uVar10;
  int local_30;
  uint local_2c;
  int local_28;
  
  uVar7 = *(undefined4 *)(param_2 + 0x1c);
  iVar8 = 0;
  iVar3 = FT_Stream_ReadUShort(param_2,&local_30);
  if (local_30 != 0) {
    return local_30;
  }
  if ((int)(uint)*(ushort *)(param_1 + 0x108) < iVar3) {
    return 3;
  }
  local_28 = param_1;
  iVar4 = ft_mem_realloc(uVar7,2,0,iVar3,0,&local_30);
  if ((local_30 == 0) && (local_30 = FT_Stream_EnterFrame(param_2,iVar3 << 1), local_30 == 0)) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  if (!bVar1) {
    for (iVar8 = 0; iVar8 < iVar3; iVar8 = iVar8 + 1) {
      uVar2 = FT_Stream_GetUShort(param_2);
      *(undefined2 *)(iVar4 + iVar8 * 2) = uVar2;
    }
    FT_Stream_ExitFrame(param_2);
    uVar9 = 0;
    for (iVar8 = 0; iVar8 < iVar3; iVar8 = iVar8 + 1) {
      uVar5 = (uint)*(ushort *)(iVar4 + iVar8 * 2);
      if ((0x101 < uVar5) && (uVar5 = uVar5 - 0x101, (int)(uVar9 & 0xffff) < (int)uVar5)) {
        uVar9 = uVar5;
      }
    }
    iVar8 = ft_mem_realloc(uVar7,4,0,uVar9 & 0xffff,0,&local_30);
    if (local_30 == 0) {
      uVar10 = 0;
      local_2c = param_3;
      while (((uint)uVar10 < (uVar9 & 0xffff) && (*(uint *)(param_2 + 8) < local_2c))) {
        uVar5 = FT_Stream_ReadChar(param_2,&local_30);
        uVar5 = uVar5 & 0xff;
        if (local_30 != 0) goto LAB_005dfeb2;
        if (((local_2c < uVar5) || (local_2c - uVar5 < *(uint *)(param_2 + 8))) &&
           (uVar5 = local_2c - *(int *)(param_2 + 8), (int)uVar5 < 0)) {
          uVar5 = 0;
        }
        uVar6 = ft_mem_realloc(uVar7,1,0,uVar5 + 1,0,&local_30);
        *(undefined4 *)(iVar8 + (uint)uVar10 * 4) = uVar6;
        if ((local_30 == 0) &&
           (local_30 = FT_Stream_Read(param_2,*(undefined4 *)(iVar8 + (uint)uVar10 * 4),uVar5),
           local_30 == 0)) {
          bVar1 = false;
        }
        else {
          bVar1 = true;
        }
        if (bVar1) goto LAB_005dfeb2;
        *(undefined1 *)(*(int *)(iVar8 + (uint)uVar10 * 4) + uVar5) = 0;
        uVar10 = uVar10 + 1;
      }
      if ((uint)uVar10 < (uVar9 & 0xffff)) {
        for (; (uint)uVar10 < (uVar9 & 0xffff); uVar10 = uVar10 + 1) {
          uVar6 = ft_mem_realloc(uVar7,1,0,1,0,&local_30);
          *(undefined4 *)(iVar8 + (uint)uVar10 * 4) = uVar6;
          if (local_30 != 0) goto LAB_005dfeb2;
          **(undefined1 **)(iVar8 + (uint)uVar10 * 4) = 0;
        }
      }
      *(short *)(local_28 + 0x27c) = (short)iVar3;
      *(short *)(local_28 + 0x27e) = (short)uVar9;
      *(int *)(local_28 + 0x280) = iVar4;
      *(int *)(local_28 + 0x284) = iVar8;
      return 0;
    }
  }
LAB_005dff3e:
  ft_mem_free(uVar7,iVar8);
  ft_mem_free(uVar7,iVar4);
  return local_30;
LAB_005dfeb2:
  for (uVar10 = 0; (uint)uVar10 < (uVar9 & 0xffff); uVar10 = uVar10 + 1) {
    ft_mem_free(uVar7,*(undefined4 *)(iVar8 + (uint)uVar10 * 4));
    *(undefined4 *)(iVar8 + (uint)uVar10 * 4) = 0;
  }
  goto LAB_005dff3e;
}

