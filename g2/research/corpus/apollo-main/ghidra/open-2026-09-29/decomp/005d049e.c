
uint FUN_005d049e(uint *param_1,uint param_2,int param_3,uint param_4,ushort *param_5)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = (uint)*param_5;
  uVar3 = *param_1;
  if (uVar3 < param_2) {
    if (param_2 - uVar3 < param_4) {
      param_4 = param_2 - uVar3;
    }
    for (uVar2 = 0; uVar2 < param_4; uVar2 = uVar2 + 1) {
      uVar1 = uVar4 >> 8;
      uVar4 = (uVar4 + *(byte *)(uVar3 + uVar2)) * 0xce6d + 0x58bf & 0xffff;
      *(byte *)(param_3 + uVar2) = *(byte *)(uVar3 + uVar2) ^ (byte)uVar1;
    }
    *param_1 = uVar3 + param_4;
    *param_5 = (ushort)uVar4;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

