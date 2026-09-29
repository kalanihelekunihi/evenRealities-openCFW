
undefined4 LvpCTCModelInitSnpuTask(undefined4 *param_1)

{
  int iVar1;
  uint uVar2;
  
  *param_1 = 0x100;
  iVar1 = iRam10208c5c;
  param_1[5] = *(uint *)(iRam10208c5c + 0x14) & 0x7ffffff;
  param_1[7] = *(uint *)(iVar1 + 0x1c) & 0x7ffffff;
  param_1[1] = *(uint *)(iVar1 + 4) & 0x7ffffff;
  uVar2 = *(uint *)(iVar1 + 0x18);
  param_1[2] = *(uint *)(iVar1 + 8) & 0x7ffffff;
  param_1[6] = uVar2 & 0x7ffffff;
  return 0;
}

