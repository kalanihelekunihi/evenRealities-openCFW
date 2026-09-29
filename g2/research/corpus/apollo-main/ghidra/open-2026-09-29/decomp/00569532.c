
int FUN_00569532(int param_1,char param_2)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 *puVar3;
  byte *pbVar4;
  undefined4 uVar5;
  int *piVar6;
  int *piVar7;
  int iVar8;
  byte *pbVar9;
  undefined4 *puVar10;
  
  piVar6 = (int *)(param_1 + 0x34);
  piVar7 = (int *)(param_1 + 0x54);
  iVar2 = 0;
  iVar8 = *piVar7 - *(int *)(param_1 + 0x68);
  if ((0 < iVar8) && (iVar2 = FUN_005682de(piVar6,iVar8), iVar2 == 0)) {
    puVar3 = (undefined4 *)(*(int *)(param_1 + 0x3c) + *piVar6 * 8);
    pbVar9 = (byte *)(*(int *)(param_1 + 0x40) + *piVar6);
    pbVar4 = (byte *)(*(int *)(param_1 + 0x60) + *piVar7);
    puVar1 = (undefined4 *)(*(int *)(param_1 + 0x5c) + *piVar7 * 8);
    while( true ) {
      puVar10 = puVar1 + -2;
      pbVar4 = pbVar4 + -1;
      if (puVar10 < (undefined4 *)(*(int *)(param_1 + 0x5c) + *(int *)(param_1 + 0x68) * 8)) break;
      uVar5 = puVar1[-1];
      *puVar3 = *puVar10;
      puVar3[1] = uVar5;
      *pbVar9 = *pbVar4;
      if (param_2 == '\0') {
        if (((*pbVar9 & 0xc) == 4) || ((*pbVar9 & 0xc) == 8)) {
          *pbVar9 = *pbVar9 ^ 0xc;
        }
      }
      else {
        *pbVar9 = *pbVar9 & 0xf3;
      }
      puVar3 = puVar3 + 2;
      pbVar9 = pbVar9 + 1;
      puVar1 = puVar10;
    }
    *piVar7 = *(int *)(param_1 + 0x68);
    *piVar6 = iVar8 + *piVar6;
    *(undefined1 *)(param_1 + 0x44) = 0;
    *(undefined1 *)(param_1 + 100) = 0;
  }
  return iVar2;
}

