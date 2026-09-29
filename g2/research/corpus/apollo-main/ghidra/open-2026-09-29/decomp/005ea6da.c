
undefined4 FUN_005ea6da(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar1 = DAT_005eb28c;
  iVar2 = td_ring_ptr();
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = (uint)*(ushort *)(iVar2 + 0x8500);
  }
  if (uVar3 < (param_1 & 0xffff)) {
    param_1 = uVar3;
  }
  if ((param_1 & 0xffff) == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *(int *)(iVar1 + (param_1 & 0xffff) * 4 + 0xbc);
  }
  for (; (param_1 & 0xffff) < uVar3; param_1 = param_1 + 1) {
    *(int *)(iVar1 + (param_1 & 0xffff) * 4 + 0xbc) = iVar2;
    iVar2 = iVar2 + (uint)*(ushort *)(iVar1 + (param_1 & 0xffff) * 2 + 0x3c);
  }
  *(int *)(iVar1 + uVar3 * 4 + 0xbc) = iVar2;
  *(int *)(iVar1 + 0x1c8) = iVar2;
  if (*(int *)(iVar1 + 8) != 0) {
    FUN_0043f4c0(*(undefined4 *)(iVar1 + 8),0x240,*(undefined4 *)(iVar1 + 0x1c8));
  }
  return param_4;
}

