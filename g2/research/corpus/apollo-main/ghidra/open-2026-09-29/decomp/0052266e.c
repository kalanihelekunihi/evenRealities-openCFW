
undefined4 FUN_0052266e(int param_1,int param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  if (param_1 != 0) {
    uVar3 = 0x4000000;
  }
  if (param_2 != 0) {
    uVar3 = uVar3 | 0x2000000;
  }
  if (param_3 != 0) {
    uVar3 = uVar3 | 0x1000000;
  }
  if (param_4 != 0) {
    uVar3 = uVar3 | 0x800000;
  }
  iVar2 = *DAT_00522f18;
  uVar1 = *(undefined4 *)(iVar2 + 0x1c);
  *(uint *)(iVar2 + 0x1c) = uVar3;
  *(uint *)(iVar2 + 0x18) =
       *(uint *)(iVar2 + 0x1c) |
       *(uint *)(iVar2 + 0x10) | *(uint *)(iVar2 + 0x14) | *(uint *)(iVar2 + 0xc);
  return uVar1;
}

