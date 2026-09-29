
uint TT_DotFix14(uint param_1,uint param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  uVar6 = param_3 * (param_1 & 0xffff);
  param_3 = param_3 * ((int)param_1 >> 0x10);
  uVar7 = uVar6 + param_3 * 0x10000;
  uVar3 = param_4 * (param_2 & 0xffff);
  param_4 = param_4 * ((int)param_2 >> 0x10);
  uVar4 = uVar3 + param_4 * 0x10000;
  uVar5 = uVar4 + uVar7;
  iVar2 = ((int)uVar3 >> 0x1f) + (param_4 >> 0x10) + (uint)(uVar4 < uVar3) +
          ((int)uVar6 >> 0x1f) + (param_3 >> 0x10) + (uint)(uVar7 < uVar6) + (uint)(uVar5 < uVar7);
  iVar1 = iVar2 >> 0x1f;
  uVar3 = iVar1 + uVar5;
  iVar1 = iVar1 + iVar2 + (uint)(uVar3 < uVar5);
  if (uVar3 + 0x2000 < uVar3) {
    iVar1 = iVar1 + 1;
  }
  return uVar3 + 0x2000 >> 0xe | iVar1 << 0x12;
}

