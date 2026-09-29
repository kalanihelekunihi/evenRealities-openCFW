
uint FUN_005d8db4(int param_1,int param_2,int param_3)

{
  byte *pbVar1;
  uint *puVar2;
  uint uVar3;
  byte *pbVar4;
  uint *puVar5;
  uint uVar6;
  
  puVar2 = (uint *)(param_2 * 0x10 + *(int *)(param_1 + 8));
  puVar5 = (uint *)(*(int *)(param_1 + 8) + param_3 * 0x10);
  pbVar1 = (byte *)puVar2[2];
  pbVar4 = (byte *)puVar5[2];
  uVar3 = *puVar2;
  uVar6 = *puVar5;
  if (uVar6 <= uVar3) {
    uVar3 = uVar6;
  }
  while( true ) {
    if (uVar3 < 8) {
      if (uVar3 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = (uint)(*pbVar1 & *pbVar4) & ~(0xff >> (uVar3 & 0xff));
      }
      return uVar3;
    }
    if ((*pbVar1 & *pbVar4) != 0) break;
    pbVar1 = pbVar1 + 1;
    pbVar4 = pbVar4 + 1;
    uVar3 = uVar3 - 8;
  }
  return 1;
}

