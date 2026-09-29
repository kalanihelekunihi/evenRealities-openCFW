
undefined2 FUN_005d94c0(byte *param_1,byte *param_2)

{
  byte bVar1;
  byte *pbVar2;
  undefined1 *puVar3;
  byte *pbVar4;
  byte *pbVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  
  if (param_1 == (byte *)0x0) {
    return 0;
  }
  if (param_2 <= param_1) {
    return 0;
  }
  pbVar2 = param_1 + 1;
  iVar8 = 0;
  uVar7 = (uint)*(byte *)(DAT_005d992c + 1);
  while( true ) {
    uVar6 = uVar7;
    if ((int)uVar6 <= iVar8) {
      return 0;
    }
    uVar7 = (int)(uVar6 + iVar8) >> 1;
    puVar3 = (undefined1 *)(DAT_005d992c + 2 + uVar7 * 2);
    pbVar4 = (byte *)((uint)CONCAT11(*puVar3,puVar3[1]) + DAT_005d992c);
    if ((*pbVar4 & 0x7f) == *param_1) break;
    if ((*pbVar4 & 0x7f) < *param_1) {
      iVar8 = uVar7 + 1;
      uVar7 = uVar6;
    }
  }
  while (pbVar2 < param_2) {
    bVar1 = *pbVar2;
    pbVar2 = pbVar2 + 1;
    if ((int)((uint)*pbVar4 << 0x18) < 0) {
      pbVar4 = pbVar4 + 1;
      if (bVar1 != (*pbVar4 & 0x7f)) {
        return 0;
      }
    }
    else {
      pbVar5 = pbVar4 + 1;
      uVar7 = *pbVar5 & 0x7f;
      if ((int)((uint)*pbVar5 << 0x18) < 0) {
        pbVar5 = pbVar4 + 3;
      }
      pbVar5 = pbVar5 + 1;
      while( true ) {
        if ((int)uVar7 < 1) {
          return 0;
        }
        pbVar4 = (byte *)((uint)CONCAT11(*pbVar5,pbVar5[1]) + DAT_005d992c);
        if (bVar1 == (*pbVar4 & 0x7f)) break;
        uVar7 = uVar7 - 1;
        pbVar5 = pbVar5 + 2;
      }
    }
  }
  if ((int)((uint)*pbVar4 << 0x18) < 0) {
    return 0;
  }
  if (-1 < (int)((uint)pbVar4[1] << 0x18)) {
    return 0;
  }
  return CONCAT11(pbVar4[2],pbVar4[3]);
}

