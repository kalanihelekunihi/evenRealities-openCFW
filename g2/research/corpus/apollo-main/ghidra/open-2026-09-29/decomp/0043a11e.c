
int * FUN_0043a11e(int *param_1)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  byte *pbVar5;
  byte *pbVar6;
  byte *pbVar7;
  byte *pbVar8;
  int iVar9;
  int unaff_r9;
  
  pbVar8 = (byte *)param_1[2];
  pbVar5 = (byte *)((int)param_1 + *param_1);
  uVar2 = param_1[1];
  pbVar7 = pbVar5;
  if ((int)(uVar2 << 0x1f) < 0) {
    pbVar8 = pbVar8 + unaff_r9;
  }
  while (pbVar7 != pbVar5 + (uVar2 >> 1)) {
    bVar1 = *pbVar7;
    uVar3 = bVar1 & 3;
    pbVar6 = pbVar7 + 1;
    if ((bVar1 & 3) == 0) {
      pbVar6 = pbVar7 + 2;
      uVar3 = pbVar7[1] + 3;
    }
    uVar4 = (uint)(bVar1 >> 4);
    if (uVar4 == 0xf) {
      uVar4 = *pbVar6 + 0xf;
      pbVar6 = pbVar6 + 1;
    }
    while (uVar3 = uVar3 - 1, uVar3 != 0) {
      *pbVar8 = *pbVar6;
      pbVar6 = pbVar6 + 1;
      pbVar8 = pbVar8 + 1;
    }
    pbVar7 = pbVar6;
    if (uVar4 != 0) {
      uVar3 = (bVar1 & 0xf) >> 2;
      pbVar7 = pbVar6 + 1;
      if (uVar3 == 3) {
        pbVar7 = pbVar6 + 2;
        uVar3 = (uint)pbVar6[1];
      }
      pbVar6 = pbVar8 + -((uint)*pbVar6 + uVar3 * 0x100);
      for (iVar9 = 0; iVar9 - 2U != uVar4; iVar9 = iVar9 + 1) {
        *pbVar8 = *pbVar6;
        pbVar6 = pbVar6 + 1;
        pbVar8 = pbVar8 + 1;
      }
    }
  }
  return param_1 + 3;
}

