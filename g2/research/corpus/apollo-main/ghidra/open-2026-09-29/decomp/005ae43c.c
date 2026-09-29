
int cff_blend_doBlend(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  int *piVar5;
  int iVar6;
  uint *puVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  int local_30;
  int local_2c;
  undefined4 uStack_28;
  
  local_2c = param_1 + 0x22c;
  local_30 = 0;
  uVar9 = *(int *)(param_1 + 0x240) * param_3;
  uVar10 = (*(int *)(param_2 + 0x14) + -4) - *(int *)(param_2 + 0x10) >> 2;
  if (uVar10 < uVar9) {
    local_30 = 0xa1;
  }
  else {
    iVar11 = param_3 * 5;
    uStack_28 = param_4;
    if (*(uint *)(param_1 + 0x25c) < (uint)(iVar11 + *(int *)(param_1 + 600))) {
      uVar8 = *(uint *)(param_1 + 0x250);
      uVar12 = *(uint *)(param_1 + 0x254);
      uVar1 = ft_mem_realloc(*(undefined4 *)(*(int *)(param_1 + 0x230) + 8),1,
                             *(undefined4 *)(param_1 + 0x25c),iVar11 + *(int *)(param_1 + 0x25c),
                             *(undefined4 *)(param_1 + 0x250),&local_30);
      *(undefined4 *)(param_1 + 0x250) = uVar1;
      if (local_30 != 0) {
        return local_30;
      }
      *(int *)(param_1 + 0x254) = *(int *)(param_1 + 0x250) + *(int *)(param_1 + 600);
      *(int *)(param_1 + 0x25c) = iVar11 + *(int *)(param_1 + 0x25c);
      if ((uVar8 != 0) && (*(uint *)(param_1 + 0x250) != uVar8)) {
        iVar2 = *(int *)(param_1 + 0x250);
        for (puVar7 = *(uint **)(param_2 + 0x10); puVar7 < *(uint **)(param_2 + 0x14);
            puVar7 = puVar7 + 1) {
          if ((uVar8 <= *puVar7) && (*puVar7 < uVar12)) {
            *puVar7 = *puVar7 + (iVar2 - uVar8);
          }
        }
      }
    }
    *(int *)(param_1 + 600) = iVar11 + *(int *)(param_1 + 600);
    iVar2 = uVar10 - uVar9;
    iVar11 = param_3 + iVar2;
    for (uVar10 = 0; uVar10 < param_3; uVar10 = uVar10 + 1) {
      piVar5 = *(int **)(local_2c + 0x18);
      iVar6 = cff_parse_num(param_2,*(int *)(param_2 + 0x10) + (iVar2 + uVar10) * 4);
      iVar6 = iVar6 << 0x10;
      for (uVar9 = 1; piVar5 = piVar5 + 1, uVar9 < *(uint *)(local_2c + 0x14); uVar9 = uVar9 + 1) {
        iVar3 = cff_parse_num(param_2,*(int *)(param_2 + 0x10) + iVar11 * 4);
        iVar11 = iVar11 + 1;
        iVar6 = *piVar5 * iVar3 + iVar6;
      }
      *(undefined4 *)(*(int *)(param_2 + 0x10) + (iVar2 + uVar10) * 4) =
           *(undefined4 *)(param_1 + 0x254);
      puVar4 = *(undefined1 **)(param_1 + 0x254);
      *(undefined1 **)(param_1 + 0x254) = puVar4 + 1;
      *puVar4 = 0xff;
      puVar4 = *(undefined1 **)(param_1 + 0x254);
      *(undefined1 **)(param_1 + 0x254) = puVar4 + 1;
      *puVar4 = (char)((uint)iVar6 >> 0x18);
      puVar4 = *(undefined1 **)(param_1 + 0x254);
      *(undefined1 **)(param_1 + 0x254) = puVar4 + 1;
      *puVar4 = (char)((uint)iVar6 >> 0x10);
      puVar4 = *(undefined1 **)(param_1 + 0x254);
      *(undefined1 **)(param_1 + 0x254) = puVar4 + 1;
      *puVar4 = (char)((uint)iVar6 >> 8);
      puVar4 = *(undefined1 **)(param_1 + 0x254);
      *(undefined1 **)(param_1 + 0x254) = puVar4 + 1;
      *puVar4 = (char)iVar6;
    }
    *(uint *)(param_2 + 0x14) = *(int *)(param_2 + 0x10) + (param_3 + iVar2) * 4;
  }
  return local_30;
}

