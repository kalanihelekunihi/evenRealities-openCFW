
undefined8 FUN_0048d4e8(uint *param_1,uint param_2)

{
  uint uVar1;
  uint *puVar2;
  uint *puVar3;
  byte *pbVar4;
  uint uVar5;
  bool bVar6;
  
  pbVar4 = (byte *)0x0;
  puVar3 = param_1;
  if (param_1 == (uint *)0x0) {
LAB_0048d53c:
    return CONCAT44(param_2,pbVar4);
  }
  while (uVar5 = (int)puVar3 << 0x1e, uVar5 != 0) {
    bVar6 = param_2 != 0;
    param_2 = param_2 - 1;
    puVar2 = puVar3;
    if (bVar6) {
      puVar2 = (uint *)((int)puVar3 + 1);
      uVar5 = (uint)(byte)*puVar3;
    }
    puVar3 = puVar2;
    if (!bVar6 || uVar5 == 0) goto LAB_0048d538;
  }
  uVar5 = 0;
  if (4 < param_2) {
    uVar5 = *puVar3;
    while( true ) {
      uVar1 = param_2 - 4;
      if (3 < param_2) {
        uVar1 = uVar5 + 0xfefefeff & ~uVar5 & 0x80808080;
      }
      if (uVar1 != 0) break;
      puVar3 = puVar3 + 1;
      uVar5 = *puVar3;
      param_2 = param_2 - 4;
    }
  }
  bVar6 = param_2 != 0;
  param_2 = param_2 - 1;
  puVar2 = puVar3;
  if (bVar6) {
    uVar5 = (uint)(byte)*puVar3;
    puVar2 = (uint *)((int)puVar3 + 1);
  }
  while( true ) {
    if (bVar6) {
      bVar6 = uVar5 != 0;
    }
    if (bVar6) {
      bVar6 = param_2 != 0;
      param_2 = param_2 - 1;
    }
    if (!bVar6) break;
    uVar5 = (uint)(byte)*puVar2;
    puVar2 = (uint *)((int)puVar2 + 1);
  }
LAB_0048d538:
  bVar6 = param_2 != 0xffffffff;
  param_2 = param_2 + 1;
  pbVar4 = (byte *)((int)puVar2 + (-(uint)bVar6 - (int)param_1));
  goto LAB_0048d53c;
}

