
undefined4 case_expand_runs(byte *param_1,byte *param_2,int param_3)

{
  byte bVar1;
  byte *pbVar2;
  uint uVar3;
  uint uVar4;
  byte *pbVar5;
  
  pbVar5 = param_2 + param_3;
  do {
    bVar1 = *param_1;
    uVar4 = bVar1 & 0xf;
    pbVar2 = param_1 + 1;
    if ((bVar1 & 0xf) == 0) {
      uVar4 = (uint)param_1[1];
      pbVar2 = param_1 + 2;
    }
    param_1 = pbVar2;
    uVar3 = (uint)(bVar1 >> 4);
    if (uVar3 == 0) {
      uVar3 = (uint)*param_1;
      param_1 = param_1 + 1;
    }
    while (uVar4 = uVar4 - 1, uVar4 != 0) {
      *param_2 = *param_1;
      param_1 = param_1 + 1;
      param_2 = param_2 + 1;
    }
    while (uVar3 = uVar3 - 1, uVar3 != 0) {
      *param_2 = 0;
      param_2 = param_2 + 1;
    }
  } while (param_2 < pbVar5);
  return 0;
}

