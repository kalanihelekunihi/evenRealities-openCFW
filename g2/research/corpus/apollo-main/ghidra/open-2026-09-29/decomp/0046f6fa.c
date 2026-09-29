
uint FUN_0046f6fa(uint *param_1)

{
  bool bVar1;
  bool bVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar5 = 0;
  uVar6 = 0;
  uVar3 = 0;
  bVar1 = false;
  uVar4 = *param_1;
  uVar7 = 0;
  bVar2 = false;
  for (uVar8 = 0; uVar8 < 0x20; uVar8 = uVar8 + 1) {
    if ((int)((uVar4 >> (uVar8 & 0xff)) << 0x1f) < 0) {
      bVar1 = true;
      uVar5 = uVar5 + 1;
    }
    else if (bVar1) {
      bVar1 = false;
      bVar2 = true;
    }
    if ((uVar8 == 0x1f) && (bVar1)) {
      bVar2 = true;
    }
    if (bVar2) {
      if (uVar6 < uVar5) {
        uVar3 = (uVar8 - 1) - (uVar5 >> 1);
        uVar7 = uVar5 & 1;
        uVar6 = uVar5;
      }
      uVar5 = 0;
      bVar2 = false;
    }
  }
  if ((uVar3 < 0x10) && ((int)(uVar4 << 0x1e) < 0)) {
    uVar3 = uVar3 - uVar7;
  }
  else if ((0xf < uVar3) && ((int)(uVar4 << 1) < 0)) {
    uVar3 = uVar3 + 1;
  }
  return uVar3;
}

