
void FUN_0052264e(int param_1)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = 0;
  if (param_1 != 0) {
    uVar1 = 0xc0000000;
  }
  iVar2 = *DAT_00522f18;
  *(uint *)(iVar2 + 0xc) = uVar1;
  *(uint *)(iVar2 + 0x18) =
       uVar1 | *(uint *)(iVar2 + 0x14) | *(uint *)(iVar2 + 0x10) | *(uint *)(iVar2 + 0x1c);
  return;
}

