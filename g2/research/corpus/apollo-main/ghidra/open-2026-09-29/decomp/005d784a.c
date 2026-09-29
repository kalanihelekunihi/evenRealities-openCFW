
int FUN_005d784a(uint *param_1,short *param_2,int param_3,uint *param_4)

{
  bool bVar1;
  undefined1 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int *piVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int *piVar12;
  int local_38;
  uint local_34;
  short *psStack_30;
  int local_2c;
  uint *local_28;
  
  psStack_30 = param_2;
  local_2c = param_3;
  local_28 = param_4;
  FUN_0043c0e4(param_1,0x80,0);
  local_34 = *local_28;
  param_1[4] = local_34;
  uVar3 = ft_mem_realloc(local_34,0x28,0,(int)param_2[1],0,&local_38);
  param_1[2] = uVar3;
  if (local_38 == 0) {
    uVar3 = ft_mem_realloc(local_34,8,0,(int)*param_2,0,&local_38);
    param_1[3] = uVar3;
    if (local_38 == 0) {
      bVar1 = false;
      goto LAB_005d78ac;
    }
  }
  bVar1 = true;
LAB_005d78ac:
  if (!bVar1) {
    *param_1 = (int)param_2[1];
    param_1[1] = (int)*param_2;
    uVar3 = param_1[2];
    piVar6 = (int *)param_1[3];
    iVar5 = 0;
    for (uVar7 = 0; uVar7 < param_1[1]; uVar7 = uVar7 + 1) {
      iVar8 = *(short *)(*(int *)(param_2 + 6) + uVar7 * 2) + 1;
      uVar4 = iVar8 - iVar5;
      *piVar6 = iVar5 * 0x28 + uVar3;
      piVar6[1] = uVar4;
      if (uVar4 != 0) {
        piVar12 = (int *)(iVar5 * 0x28 + uVar3);
        *piVar12 = iVar8 * 0x28 + uVar3 + -0x28;
        piVar12[2] = (int)piVar6;
        for (; 1 < uVar4; uVar4 = uVar4 - 1) {
          piVar12[1] = (int)(piVar12 + 10);
          piVar12[10] = (int)piVar12;
          piVar12[0xc] = (int)piVar6;
          piVar12 = piVar12 + 10;
        }
        piVar12[1] = uVar3 + iVar5 * 0x28;
      }
      piVar6 = piVar6 + 2;
      iVar5 = iVar8;
    }
    piVar12 = (int *)param_1[2];
    iVar5 = *(int *)(param_2 + 2);
    piVar6 = piVar12;
    for (uVar3 = 0; iVar8 = local_2c, uVar3 < *param_1; uVar3 = uVar3 + 1) {
      iVar8 = (*piVar12 - (int)piVar6) / 0x28;
      iVar10 = (piVar12[1] - (int)piVar6) / 0x28;
      if (-1 < (int)((uint)*(byte *)(*(int *)(param_2 + 4) + uVar3) << 0x1f)) {
        piVar12[3] = 1;
      }
      iVar9 = *(int *)(iVar5 + uVar3 * 8) - *(int *)(iVar5 + iVar8 * 8);
      iVar8 = *(int *)(iVar5 + uVar3 * 8 + 4) - *(int *)(iVar5 + iVar8 * 8 + 4);
      uVar2 = FUN_005d7782(iVar9,iVar8);
      *(undefined1 *)(piVar12 + 5) = uVar2;
      iVar11 = *(int *)(iVar5 + iVar10 * 8) - *(int *)(iVar5 + uVar3 * 8);
      iVar10 = *(int *)(iVar5 + iVar10 * 8 + 4) - *(int *)(iVar5 + uVar3 * 8 + 4);
      uVar2 = FUN_005d7782(iVar11,iVar10);
      *(undefined1 *)((int)piVar12 + 0x15) = uVar2;
      if ((int)((uint)*(byte *)(piVar12 + 3) << 0x1f) < 0) {
        piVar12[3] = piVar12[3] | 2;
      }
      else if (((char)piVar12[5] == *(char *)((int)piVar12 + 0x15)) &&
              ((*(char *)((int)piVar12 + 0x15) != '\x04' ||
               (iVar8 = ft_corner_is_flat(iVar9,iVar8,iVar11,iVar10), iVar8 != 0)))) {
        piVar12[3] = piVar12[3] | 2;
      }
      piVar12 = piVar12 + 10;
    }
    param_1[5] = (uint)param_2;
    param_1[6] = (uint)local_28;
    FUN_005d77ca(param_1,0);
    FUN_005d761a(param_1);
    local_38 = FUN_005d71c4(param_1 + 7,iVar8 + 0x10,iVar8 + 0x1c,iVar8 + 0x28,local_34);
    if (local_38 == 0) {
      local_38 = FUN_005d71c4(param_1 + 0x11,iVar8 + 0x34,iVar8 + 0x40,iVar8 + 0x4c,local_34);
    }
  }
  return local_38;
}

