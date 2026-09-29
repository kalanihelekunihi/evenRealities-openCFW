
uint * FUN_0044b5a0(uint *param_1,uint *param_2,uint param_3)

{
  uint *puVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  puVar2 = param_1;
  if (((uint)param_2 & 3) != 0) {
    puVar1 = param_1;
    puVar3 = param_2;
    uVar4 = param_3;
    if (param_3 < 4) goto LAB_0044b5f4;
    do {
      param_2 = (uint *)((int)puVar3 + 1);
      uVar5 = *puVar3;
      uVar4 = uVar4 - 1;
      puVar2 = (uint *)((int)puVar1 + 1);
      *(char *)puVar1 = (char)uVar5;
      if ((char)uVar5 == '\0') goto LAB_0044b604;
      puVar1 = puVar2;
      puVar3 = param_2;
      param_3 = uVar4;
    } while (((uint)param_2 & 3) != 0);
  }
  puVar1 = puVar2;
  if (((uint)puVar2 & 3) == 0) {
    while (uVar4 = param_3 - 4, 3 < param_3) {
      uVar5 = *param_2;
      uVar6 = uVar5 + 0xfefefeff & ~uVar5;
      uVar7 = uVar6 & 0x80808080;
      if (uVar7 != 0) {
        uVar6 = 0x18 - LZCOUNT((uVar6 & 0x80) << 0x18 | (uVar7 >> 8 & 0xff) << 0x10 |
                               (uVar7 >> 0x10 & 0xff) << 8 | uVar7 >> 0x18);
        puVar2 = puVar1 + 1;
        *puVar1 = (uVar5 << (uVar6 & 0xff)) >> (uVar6 & 0xff);
        goto LAB_0044b604;
      }
      *puVar1 = uVar5;
      puVar1 = puVar1 + 1;
      param_2 = param_2 + 1;
      param_3 = uVar4;
    }
  }
LAB_0044b5f4:
  uVar4 = param_3;
  if (param_3 != 0) {
    do {
      uVar5 = *param_2;
      uVar4 = uVar4 - 1;
      puVar2 = (uint *)((int)puVar1 + 1);
      *(char *)puVar1 = (char)uVar5;
      if ((char)uVar5 == '\0') break;
      puVar1 = puVar2;
      param_2 = (uint *)((int)param_2 + 1);
    } while (uVar4 != 0);
LAB_0044b604:
    if (uVar4 != 0) {
      FUN_0043c0ec(puVar2,uVar4,0);
    }
  }
  return param_1;
}

