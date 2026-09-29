
undefined8 FUN_0059c7ac(uint param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  bool bVar7;
  
  uVar5 = param_2 & 0x80000000;
  if ((int)uVar5 < 0) {
    bVar7 = param_1 != 0;
    param_1 = -param_1;
    param_2 = -(uint)bVar7 - param_2;
  }
  if (param_2 != 0) {
    uVar1 = param_1 << LZCOUNT(param_2);
    iVar2 = -LZCOUNT(param_2);
    uVar4 = iVar2 + 0x20U & 0x1f;
    uVar3 = ((param_2 ^ param_1) >> uVar4 | (param_2 ^ param_1) << 0x20 - uVar4) ^ uVar1;
    uVar6 = uVar1 >> 0xb;
    bVar7 = 0x80000000 < uVar1 * 0x200000 ||
            uVar1 * 0x200000 + 0x80000000 < (uint)((uVar1 & 0x800) != 0);
    uVar4 = uVar3 * 0x200000;
    return CONCAT44((uVar5 | (iVar2 + 0x43d) * 0x100000) +
                    (uVar3 >> 0xb) +
                    (uint)(CARRY4(uVar6,uVar4) || CARRY4(uVar6 + uVar4,(uint)bVar7)),
                    uVar6 + uVar4 + bVar7);
  }
  uVar4 = 0;
  iVar2 = 0;
  if (param_1 != 0) {
    uVar1 = param_1 << LZCOUNT(param_1);
    uVar4 = LZCOUNT(param_1) * -0x100000 + 0x41d00000 + (uVar1 >> 0xb) | uVar5;
    iVar2 = uVar1 << 0x15;
  }
  return CONCAT44(uVar4,iVar2);
}

