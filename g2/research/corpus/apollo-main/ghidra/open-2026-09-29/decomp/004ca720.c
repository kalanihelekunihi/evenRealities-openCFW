
int lfs_npw2(int param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = (uint)(0xffff < param_1 - 1U) << 4;
  uVar1 = param_1 - 1U >> uVar2;
  uVar3 = (uint)(0xff < uVar1) << 3;
  uVar1 = uVar1 >> uVar3;
  uVar4 = (uint)(0xf < uVar1) << 2;
  uVar1 = uVar1 >> uVar4;
  uVar5 = (uint)(3 < uVar1) << 1;
  return (uVar2 | uVar3 | uVar4 | uVar5 | (uVar1 >> uVar5) >> 1) + 1;
}

