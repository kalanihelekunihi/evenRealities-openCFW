
uint FUN_004506fc(uint param_1,int param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = param_1;
  if ((int)param_1 < 0) {
    if (param_2 - param_3 < 1) {
      param_2 = param_3 - param_2;
    }
    else {
      param_2 = param_2 - param_3;
    }
    uVar2 = (uint)(param_2 * 100) / (param_1 & 0x3ff);
    uVar3 = (param_1 & 0x3fffffff) >> 0x14;
    uVar1 = (param_1 & 0xfffff) >> 10;
    uVar4 = uVar2;
    if (uVar3 * 10 <= uVar2) {
      uVar4 = uVar3 * 10;
    }
    if (uVar4 < uVar1 * 10) {
      uVar2 = uVar1 * 10;
    }
    else if (uVar3 * 10 <= uVar2) {
      uVar2 = uVar3 * 10;
    }
  }
  return uVar2;
}

