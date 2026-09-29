
void FUN_005d761a(int param_1)

{
  bool bVar1;
  uint uVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  int *piVar10;
  int iVar11;
  int *piVar12;
  int *piVar13;
  uint local_34;
  int local_30;
  
  local_34 = 0;
  do {
    if (*(uint *)(param_1 + 4) <= local_34) {
      return;
    }
    bVar1 = false;
    if (3 < *(uint *)(*(int *)(param_1 + 0xc) + local_34 * 8 + 4)) {
      piVar3 = *(int **)(*(int *)(param_1 + 0xc) + local_34 * 8);
      piVar10 = piVar3;
      do {
        piVar10 = (int *)piVar10[1];
        if (piVar10 == piVar3) goto LAB_005d769e;
        iVar8 = piVar10[7];
        iVar4 = piVar3[7];
        iVar7 = piVar10[8];
        iVar5 = piVar3[8];
        piVar13 = piVar3;
      } while (iVar7 - iVar5 == 0 && iVar8 - iVar4 == 0);
      do {
        piVar12 = piVar13;
        piVar13 = (int *)*piVar12;
        if (piVar13 == piVar3) goto LAB_005d769e;
        local_30 = piVar12[7] - piVar13[7];
        iVar11 = piVar12[8] - piVar13[8];
      } while ((iVar11 == 0 && local_30 == 0) ||
              (uVar6 = ft_corner_orientation(iVar8 - iVar4,iVar7 - iVar5,local_30,iVar11),
              piVar9 = piVar12, uVar6 == 0));
      do {
        do {
          piVar3 = piVar10;
          piVar10 = (int *)piVar3[1];
          if (piVar10 == piVar12) {
            bVar1 = true;
          }
          iVar4 = piVar10[7] - piVar3[7];
          iVar5 = piVar10[8] - piVar3[8];
        } while ((iVar5 == 0 && iVar4 == 0) ||
                (uVar2 = ft_corner_orientation(local_30,iVar11,iVar4,iVar5), uVar2 == 0));
        if ((int)(uVar6 ^ uVar2) < 0) {
          do {
            piVar9[3] = piVar9[3] | 4;
            piVar9 = (int *)piVar9[1];
          } while (piVar9 != piVar3);
          piVar9[3] = piVar9[3] | 4;
        }
        uVar6 = uVar2;
        iVar11 = iVar5;
        piVar9 = piVar3;
        local_30 = iVar4;
      } while (!bVar1);
    }
LAB_005d769e:
    local_34 = local_34 + 1;
  } while( true );
}

