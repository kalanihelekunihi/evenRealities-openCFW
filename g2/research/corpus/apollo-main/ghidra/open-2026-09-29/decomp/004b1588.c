
void FUN_004b1588(int param_1)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = 0;
  if (param_1 != 0) {
    uVar1 = 0x8000000;
  }
  iVar2 = *DAT_004b178c;
  *(uint *)(iVar2 + 0x14) = uVar1;
  *(uint *)(iVar2 + 0x18) =
       *(uint *)(iVar2 + 0xc) | uVar1 | *(uint *)(iVar2 + 0x10) | *(uint *)(iVar2 + 0x1c);
  return;
}

