
int FUN_005d8e02(uint *param_1,uint param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  byte *pbVar2;
  byte *pbVar3;
  uint uVar4;
  uint uVar5;
  uint *puVar6;
  uint *puVar7;
  uint uVar8;
  uint *puStack_30;
  uint uStack_2c;
  uint uStack_28;
  undefined4 uStack_24;
  
  uVar4 = param_2;
  uVar5 = param_3;
  if (param_3 < param_2) {
    uVar4 = param_3;
    uVar5 = param_2;
  }
  if ((uVar4 < uVar5) && (uVar5 < *param_1)) {
    puVar7 = (uint *)(param_1[2] + uVar4 * 0x10);
    puVar6 = (uint *)(param_1[2] + uVar5 * 0x10);
    uVar8 = *puVar7;
    uVar4 = *puVar6;
    puStack_30 = param_1;
    uStack_2c = param_2;
    uStack_28 = param_3;
    uStack_24 = param_4;
    if (uVar4 != 0) {
      if (uVar8 < uVar4) {
        iVar1 = FUN_005d8bc0(puVar7,uVar4,param_4);
        if (iVar1 != 0) {
          return iVar1;
        }
        for (; uVar8 < uVar4; uVar8 = uVar8 + 1) {
          FUN_005d8c1e(puVar7,uVar8);
        }
      }
      pbVar2 = (byte *)puVar6[2];
      pbVar3 = (byte *)puVar7[2];
      for (uVar4 = uVar4 + 7 >> 3; uVar4 != 0; uVar4 = uVar4 - 1) {
        *pbVar3 = *pbVar3 | *pbVar2;
        pbVar3 = pbVar3 + 1;
        pbVar2 = pbVar2 + 1;
      }
    }
    *puVar6 = 0;
    puVar6[3] = 0;
    iVar1 = (*param_1 - 1) - uVar5;
    if (0 < iVar1) {
      FUN_00439c04(&puStack_30,puVar6,0x10);
      FUN_00439710(puVar6,puVar6 + 4,iVar1 * 0x10);
      FUN_00439c04(puVar6 + iVar1 * 4,&puStack_30,0x10);
    }
    *param_1 = *param_1 - 1;
  }
  return 0;
}

