
int FUN_005d87fa(uint param_1,int param_2,short param_3)

{
  uint uVar1;
  short sVar2;
  
  for (uVar1 = 0; uVar1 < param_1; uVar1 = uVar1 + 2) {
    sVar2 = *(short *)(param_2 + uVar1 * 2 + 2) - *(short *)(param_2 + uVar1 * 2);
    if (param_3 < sVar2) {
      param_3 = sVar2;
    }
  }
  return (int)param_3;
}

