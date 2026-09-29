
uint TT_MulFix14(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = param_2 ^ param_1;
  if ((int)param_1 < 0) {
    param_1 = -param_1;
  }
  if ((int)param_2 < 0) {
    param_2 = -param_2;
  }
  uVar2 = param_2 * (param_1 >> 0x10);
  uVar1 = uVar2 >> 0x10;
  uVar2 = uVar2 * 0x10000 + 0x2000;
  uVar3 = uVar2 + param_2 * (param_1 & 0xffff);
  if (uVar3 < uVar2) {
    uVar1 = uVar1 + 1;
  }
  uVar1 = uVar1 << 0x12 | uVar3 >> 0xe;
  if ((int)uVar4 < 0) {
    uVar1 = -uVar1;
  }
  return uVar1;
}

