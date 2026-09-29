
undefined4 FUN_005e093a(int param_1,byte *param_2,byte *param_3,uint param_4,int param_5)

{
  byte bVar1;
  undefined4 uVar2;
  uint uVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  byte *pbVar9;
  byte *pbVar10;
  
  uVar2 = 0;
  puVar4 = *(uint **)(param_1 + 8);
  uVar6 = puVar4[2];
  uVar8 = (uint)*(ushort *)(*(int *)(param_1 + 0xc) + 2);
  uVar5 = (uint)**(ushort **)(param_1 + 0xc);
  uVar7 = *(byte *)(param_1 + 0x12) * uVar8;
  if (((((int)param_4 < 0) || (puVar4[1] < uVar8 + param_4)) || (param_5 < 0)) ||
     (*puVar4 < uVar5 + param_5)) {
    uVar2 = 3;
  }
  else if (param_3 < param_2 + uVar5 * ((int)(uVar7 + 7) >> 3)) {
    uVar2 = 3;
  }
  else {
    pbVar9 = (byte *)(puVar4[3] + uVar6 * param_5 + ((int)param_4 >> 3));
    param_4 = param_4 & 7;
    if (param_4 == 0) {
      for (; pbVar10 = pbVar9, uVar8 = uVar7, 0 < (int)uVar5; uVar5 = uVar5 - 1) {
        for (; 7 < (int)uVar8; uVar8 = uVar8 - 8) {
          *pbVar10 = *param_2 | *pbVar10;
          param_2 = param_2 + 1;
          pbVar10 = pbVar10 + 1;
        }
        if (0 < (int)uVar8) {
          *pbVar10 = (byte)(0xff00 >> (uVar8 & 0xff)) & *param_2 | *pbVar10;
          param_2 = param_2 + 1;
        }
        pbVar9 = pbVar9 + uVar6;
      }
    }
    else {
      for (; 0 < (int)uVar5; uVar5 = uVar5 - 1) {
        uVar3 = 0;
        pbVar10 = pbVar9;
        for (uVar8 = uVar7; 7 < (int)uVar8; uVar8 = uVar8 - 8) {
          bVar1 = *param_2;
          param_2 = param_2 + 1;
          *pbVar10 = (byte)((uVar3 | bVar1) >> param_4) | *pbVar10;
          pbVar10 = pbVar10 + 1;
          uVar3 = (uVar3 | bVar1) << 8;
        }
        if (0 < (int)uVar8) {
          uVar3 = uVar3 | 0xff00U >> (uVar8 & 0xff) & (uint)*param_2;
          param_2 = param_2 + 1;
        }
        *pbVar10 = (byte)(uVar3 >> param_4) | *pbVar10;
        if (8 < (int)(uVar8 + param_4)) {
          pbVar10[1] = (byte)((uVar3 << 8) >> param_4) | pbVar10[1];
        }
        pbVar9 = pbVar9 + uVar6;
      }
    }
  }
  return uVar2;
}

