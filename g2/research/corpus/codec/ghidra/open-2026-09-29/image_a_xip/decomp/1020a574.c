
uint gx8002_pack_double(uint *param_1)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  
  uVar3 = *param_1;
  uVar5 = param_1[3];
  uVar6 = param_1[4];
  if (uVar3 < 2) {
    return uVar6 << 0x18 | uVar5 >> 8;
  }
  if (((uVar3 != 4) && (uVar3 != 2)) && (uVar5 != 0 || uVar6 != 0)) {
    uVar3 = param_1[2];
    if ((int)uVar3 < -0x3fe) {
      uVar4 = -uVar3 - 0x3fe;
      if ((int)uVar4 < 0x39) {
        uVar2 = -uVar3 - 0x41e;
        bVar1 = (uVar2 & 0x80000000) == 0;
        uVar3 = uVar5 >> (uVar4 & 0x3f) | (uVar6 << 1) << (0x1f - uVar4 & 0x3f);
        if (bVar1) {
          uVar3 = uVar6 >> (uVar2 & 0x3f);
        }
        iVar7 = 1 << (uVar4 & 0x3f);
        uVar8 = uVar6 >> (uVar4 & 0x3f);
        uVar4 = 0;
        if (bVar1) {
          iVar7 = 0;
          uVar8 = 0;
          uVar4 = 1 << (uVar2 & 0x3f);
        }
        if (iVar7 == 0) {
          uVar4 = uVar4 - 1;
        }
        uVar5 = (uint)((uVar5 & iVar7 - 1U) != 0 || (uVar6 & uVar4) != 0);
        uVar6 = uVar3 | uVar5;
        if ((uVar3 & 0xff | uVar5) == 0x80) {
          if ((uVar3 & 0x100) == 0) {
            return uVar3 >> 8 | uVar8 << 0x18;
          }
          uVar5 = 0x80;
        }
        else {
          uVar5 = 0x7f;
        }
        return uVar6 + uVar5 >> 8 | (uVar8 + CARRY4(uVar6,uVar5)) * 0x1000000;
      }
    }
    else if ((int)uVar3 < 0x400) {
      if ((uVar5 & 0xff) == 0x80) {
        if ((uVar5 & 0x100) != 0) {
          bVar1 = 0xffffff7f < uVar5;
          uVar5 = uVar5 + 0x80;
          uVar6 = uVar6 + bVar1;
        }
      }
      else {
        bVar1 = 0xffffff80 < uVar5;
        uVar5 = uVar5 + 0x7f;
        uVar6 = uVar6 + bVar1;
      }
      if (0x1fffffff < uVar6) {
        uVar3 = uVar6 << 0x1f;
        uVar6 = uVar6 >> 1;
        uVar5 = uVar3 | uVar5 >> 1;
      }
      return uVar5 >> 8 | uVar6 << 0x18;
    }
  }
  return 0;
}

