
void ft_trig_pseudo_rotate(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  
  iVar7 = *param_1;
  iVar6 = param_1[1];
  for (; param_2 < -0x2d0000; param_2 = (int)&DAT_005a0000 + param_2) {
    iVar5 = -iVar7;
    iVar7 = iVar6;
    iVar6 = iVar5;
  }
  for (; iVar5 = iVar7, DAT_0052912c <= param_2; param_2 = param_2 + -0x5a0000) {
    iVar7 = -iVar6;
    iVar6 = iVar5;
  }
  iVar7 = 1;
  piVar8 = DAT_00529130;
  for (uVar3 = 1; (int)uVar3 < 0x17; uVar3 = uVar3 + 1) {
    if (param_2 < 0) {
      iVar1 = iVar7 + iVar6 >> (uVar3 & 0xff);
      iVar4 = -(iVar7 + iVar5 >> (uVar3 & 0xff));
      iVar2 = *piVar8;
    }
    else {
      iVar1 = -(iVar7 + iVar6 >> (uVar3 & 0xff));
      iVar4 = iVar7 + iVar5 >> (uVar3 & 0xff);
      iVar2 = -*piVar8;
    }
    iVar6 = iVar6 + iVar4;
    iVar5 = iVar1 + iVar5;
    piVar8 = piVar8 + 1;
    param_2 = iVar2 + param_2;
    iVar7 = iVar7 << 1;
  }
  *param_1 = iVar5;
  param_1[1] = iVar6;
  return;
}

