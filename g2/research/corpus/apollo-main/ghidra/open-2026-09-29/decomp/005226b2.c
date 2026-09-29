
undefined4 FUN_005226b2(uint param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = *DAT_00522f18;
  uVar1 = *(undefined4 *)(iVar2 + 0x1c);
  *(uint *)(iVar2 + 0x1c) = param_1 & 0x7800000;
  *(uint *)(iVar2 + 0x18) =
       param_1 & 0x7800000 |
       *(uint *)(iVar2 + 0xc) | *(uint *)(iVar2 + 0x14) | *(uint *)(iVar2 + 0x10);
  return uVar1;
}

