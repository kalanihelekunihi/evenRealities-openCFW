
void ft_trig_pseudo_polarize(int *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  
  iVar5 = *param_1;
  iVar8 = param_1[1];
  if (iVar5 < iVar8) {
    if (-iVar5 < iVar8) {
      puVar3 = &DAT_005a0000;
      iVar7 = iVar8;
      iVar8 = -iVar5;
    }
    else {
      puVar3 = DAT_00529134;
      if (0 < iVar8) {
        puVar3 = (undefined4 *)0xb40000;
      }
      iVar7 = -iVar5;
      iVar8 = -iVar8;
    }
  }
  else if (iVar8 + iVar5 < 0 == SCARRY4(iVar8,iVar5)) {
    puVar3 = (undefined4 *)0x0;
    iVar7 = iVar5;
  }
  else {
    puVar3 = DAT_00529138;
    iVar7 = -iVar8;
    iVar8 = iVar5;
  }
  iVar5 = 1;
  piVar9 = DAT_00529130;
  for (uVar4 = 1; (int)uVar4 < 0x17; uVar4 = uVar4 + 1) {
    if (iVar8 < 1) {
      iVar1 = -(iVar5 + iVar8 >> (uVar4 & 0xff));
      iVar6 = iVar5 + iVar7 >> (uVar4 & 0xff);
      iVar2 = -*piVar9;
    }
    else {
      iVar1 = iVar5 + iVar8 >> (uVar4 & 0xff);
      iVar6 = -(iVar5 + iVar7 >> (uVar4 & 0xff));
      iVar2 = *piVar9;
    }
    iVar8 = iVar8 + iVar6;
    iVar7 = iVar1 + iVar7;
    piVar9 = piVar9 + 1;
    puVar3 = (undefined4 *)(iVar2 + (int)puVar3);
    iVar5 = iVar5 << 1;
  }
  if ((int)puVar3 < 0) {
    uVar4 = -(8U - (int)puVar3 & 0xfffffff0);
  }
  else {
    uVar4 = (uint)(puVar3 + 2) & 0xfffffff0;
  }
  *param_1 = iVar7;
  param_1[1] = uVar4;
  return;
}

