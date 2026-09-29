
void FUN_00584a38(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = DAT_00584e44;
  *(undefined4 *)(DAT_00584e44 + 0x48) = 0;
  *(undefined4 *)(iVar1 + 0x4c) = param_1;
  *(undefined4 *)(iVar1 + 0x50) = param_2;
  *(uint *)(iVar1 + 0x38) = *(uint *)(iVar1 + 0x38) | 0x1800;
  *(undefined4 *)(iVar1 + 0x44) = 0x1821;
  *(uint *)(iVar1 + 4) = *(uint *)(iVar1 + 4) & 0xffffffcf;
  DataMemoryBarrier(0x1f);
  *(undefined4 *)(iVar1 + 0x48) = 10;
  return;
}

