
void FUN_00568728(int *param_1,short *param_2)

{
  int iVar1;
  byte *pbVar2;
  undefined1 *puVar3;
  short *psVar4;
  short sVar5;
  
  if (*param_1 != 0) {
    FUN_00439be4(*(int *)(param_2 + 2) + param_2[1] * 8,param_1[2],*param_1 << 3);
  }
  pbVar2 = (byte *)param_1[3];
  puVar3 = (undefined1 *)(*(int *)(param_2 + 4) + (int)param_2[1]);
  for (iVar1 = *param_1; iVar1 != 0; iVar1 = iVar1 + -1) {
    if ((int)((uint)*pbVar2 << 0x1f) < 0) {
      *puVar3 = 1;
    }
    else if ((int)((uint)*pbVar2 << 0x1e) < 0) {
      *puVar3 = 2;
    }
    else {
      *puVar3 = 0;
    }
    pbVar2 = pbVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  pbVar2 = (byte *)param_1[3];
  psVar4 = (short *)(*(int *)(param_2 + 6) + *param_2 * 2);
  sVar5 = param_2[1];
  for (iVar1 = *param_1; iVar1 != 0; iVar1 = iVar1 + -1) {
    if ((int)((uint)*pbVar2 << 0x1c) < 0) {
      *psVar4 = sVar5;
      psVar4 = psVar4 + 1;
      *param_2 = *param_2 + 1;
    }
    pbVar2 = pbVar2 + 1;
    sVar5 = sVar5 + 1;
  }
  param_2[1] = (short)*param_1 + param_2[1];
  return;
}

