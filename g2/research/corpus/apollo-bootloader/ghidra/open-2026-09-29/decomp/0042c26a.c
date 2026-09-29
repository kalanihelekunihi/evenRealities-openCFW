
undefined8 hw_clock_encode_42c26a(uint param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  
  uVar2 = DAT_0042c980;
  if (param_1 == 0) {
    uVar3 = 0;
    uVar4 = 0;
  }
  else {
    uVar4 = (uint)(DAT_0042c980 != param_1 * (DAT_0042c980 / param_1)) + DAT_0042c980 / param_1;
    uVar3 = 0x1f - LZCOUNT(-uVar4 & uVar4);
    if (6 < (int)uVar3) {
      uVar3 = 6;
    }
    if ((param_1 < DAT_0042c980 >> 0xe) ||
       ((DAT_0042c980 / 3 <= param_1 && (param_1 <= (DAT_0042c980 >> 1) - 1)))) {
      iVar7 = 1;
    }
    else {
      iVar7 = 0;
    }
    uVar5 = (iVar7 * 2 + 1) * (1 << (uVar3 & 0xff));
    uVar9 = uVar4 / uVar5;
    if (uVar4 != uVar5 * (uVar4 / uVar5)) {
      uVar9 = uVar9 + 1;
    }
    iVar6 = -LZCOUNT(uVar9);
    uVar5 = iVar6 + 0x1f;
    if (7 < uVar5) {
      uVar3 = (uVar3 + uVar5) - 7;
    }
    uVar8 = uVar3 + 1;
    if (uVar8 < 8) {
      uVar10 = uVar9;
      if ((7 < uVar5) &&
         (uVar10 = uVar9 >> (iVar6 + 0x118U & 0xff), uVar5 = 1 << (iVar6 + 0x18U & 0xff),
         uVar9 != uVar5 * (uVar9 / uVar5))) {
        uVar10 = uVar10 + 1;
      }
      if ((param_1 < DAT_0042c980 >> 2) && (1 << (uVar3 + 0x100 & 0xff) != uVar4)) {
        iVar6 = 1;
      }
      else {
        iVar6 = 0;
      }
      if (param_2 == 1) {
        iVar1 = -2;
      }
      else {
        iVar1 = -1;
      }
      uVar3 = (uVar10 + iVar1 >> 1 & 0xff) << 0x10 |
              uVar8 * 0x100 & 0xf00 | iVar7 << 0xc | iVar6 << 0xd | (uVar10 - 1) * 0x1000000;
      uVar4 = rounded_divider_42c222(DAT_0042c980,uVar8,iVar7,iVar6,uVar10 - 1,param_4);
      if ((uVar4 == DAT_0042c984 * (uVar4 / DAT_0042c984)) &&
         (iVar7 = is_power_of_two_42c256(uVar4 / DAT_0042c984), iVar7 != 0)) {
        uVar4 = rounded_divider_42c222(uVar2,uVar8,1,0,0,param_4);
        uVar3 = uVar8 * 0x100 & 0xf00 | 0x1000;
      }
    }
    else {
      uVar3 = 0;
      uVar4 = 0;
    }
  }
  return CONCAT44(uVar4,uVar3);
}

