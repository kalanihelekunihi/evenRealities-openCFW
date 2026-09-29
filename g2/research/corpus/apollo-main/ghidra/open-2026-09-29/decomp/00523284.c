
void FUN_00523284(void)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  piVar1 = DAT_005232d0;
  iVar2 = *DAT_005232d0;
  uVar3 = *(uint *)(iVar2 + 0x1c);
  *(undefined4 *)(iVar2 + 0x1c) = 0x5000000;
  uVar3 = uVar3 & 0x7800000;
  *(uint *)(iVar2 + 0x18) =
       *(uint *)(iVar2 + 0xc) | *(uint *)(iVar2 + 0x14) | *(uint *)(iVar2 + 0x10) | 0x5000000;
  FUN_00522fb4();
  iVar2 = *piVar1;
  *(uint *)(iVar2 + 0x1c) = uVar3;
  *(uint *)(iVar2 + 0x18) =
       uVar3 | *(uint *)(iVar2 + 0xc) | *(uint *)(iVar2 + 0x14) | *(uint *)(iVar2 + 0x10);
  return;
}

