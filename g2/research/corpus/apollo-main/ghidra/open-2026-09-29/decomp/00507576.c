
uint FUN_00507576(undefined4 param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  byte bVar3;
  byte bVar4;
  
  uVar1 = 0;
  for (bVar3 = 0; bVar3 < 3; bVar3 = bVar3 + 1) {
    for (bVar4 = 0; bVar4 < 3; bVar4 = bVar4 + 1) {
      uVar2 = FUN_00508e92(param_1,(uint)bVar3 * 0xc + (uint)bVar4 * 4 + 0x264,4,
                           (uint)bVar3 * 0xc + param_2 + (uint)bVar4 * 4);
      uVar1 = uVar2 | uVar1;
    }
  }
  return uVar1;
}

