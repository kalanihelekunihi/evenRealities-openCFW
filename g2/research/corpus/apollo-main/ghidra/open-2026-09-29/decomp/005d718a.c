
undefined4 FUN_005d718a(undefined4 param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  byte *pbVar3;
  uint uVar4;
  uint uVar5;
  
  uVar1 = 0;
  uVar2 = 0;
  pbVar3 = (byte *)param_2[2];
  uVar5 = *param_2;
  for (uVar4 = 0; uVar4 < uVar5; uVar4 = uVar4 + 1) {
    if (uVar1 == 0) {
      uVar2 = (uint)*pbVar3;
      pbVar3 = pbVar3 + 1;
      uVar1 = 0x80;
    }
    if ((uVar2 & uVar1) != 0) {
      FUN_005d7124(param_1,uVar4);
    }
    uVar1 = (int)uVar1 >> 1;
  }
  return param_4;
}

