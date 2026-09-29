
uint FUN_10006fec(uint param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 *puVar4;
  uint uVar5;
  uint uVar6;
  int *piVar7;
  byte *pbVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  byte bStack_25;
  byte bStack_24;
  byte bStack_23;
  
  iVar1 = DAT_100070f4;
  iVar3 = *(int *)(DAT_100070f4 + 0xc);
  bStack_24 = 0;
  bStack_23 = 0;
  *param_2 = 0;
  piVar7 = *(int **)(iVar3 + 0x10);
  if ((piVar7 == (int *)0x0) || (*piVar7 == 0)) {
    return -(uint)(param_1 != 0);
  }
  uVar11 = *(uint *)(iVar3 + 4);
  do {
    FUN_10006c30(5,&bStack_25,1);
    uVar9 = bStack_25 & 1;
  } while ((bStack_25 & 1) != 0);
  puVar4 = *(undefined4 **)(*(int *)(iVar1 + 0xc) + 0x10);
  uVar2 = puVar4[1];
  pbVar8 = (byte *)*puVar4;
  uVar10 = uVar9;
  uVar12 = uVar9;
  uVar13 = uVar9;
  if (uVar2 != 0) {
    uVar5 = *(uint *)(pbVar8 + 4);
    uVar6 = uVar9;
    while (uVar5 <= param_1) {
      uVar6 = uVar6 + 1;
      uVar9 = (uint)*pbVar8;
      uVar10 = (uint)pbVar8[2];
      uVar13 = (uint)pbVar8[1];
      uVar12 = (uint)pbVar8[3];
      if (uVar6 == uVar2) break;
      uVar5 = *(uint *)(pbVar8 + 0xc);
      pbVar8 = pbVar8 + 8;
    }
  }
  uVar11 = uVar11 >> 0x10;
  if ((uVar11 == 0x5e) || (uVar11 == 0x85)) {
    FUN_10006c30(5,&bStack_25,1);
    bStack_24 = (byte)uVar9 | bStack_25 & ~(byte)uVar13;
    FUN_10006c30(0x35,&bStack_25,1);
    bStack_23 = (byte)uVar10 | bStack_25 & ~(byte)uVar12;
    FUN_10006d34(&bStack_24,2,1);
    do {
      FUN_10006c30(5,&bStack_25,1);
    } while ((bStack_25 & 1) != 0);
    uVar11 = FUN_10006f04();
    if (uVar11 != 0xffffffff) {
      *param_2 = uVar11;
      uVar11 = bStack_25 & 1;
    }
  }
  else {
    uVar11 = 0xffffffff;
  }
  return uVar11;
}

