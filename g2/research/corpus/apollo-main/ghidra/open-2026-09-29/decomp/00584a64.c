
void FUN_00584a64(void)

{
  int iVar1;
  
  iVar1 = DAT_00584e44;
  *(undefined4 *)(DAT_00584e44 + 0x48) = 0;
  *(uint *)(iVar1 + 4) = *(uint *)(iVar1 + 4) & 0xffffffcf;
  *(undefined4 *)(iVar1 + 0x44) = 0x1800;
  return;
}

