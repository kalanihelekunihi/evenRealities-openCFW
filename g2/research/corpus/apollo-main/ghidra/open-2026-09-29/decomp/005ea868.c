
uint FUN_005ea868(int param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  iVar1 = DAT_005eb28c;
  iVar2 = td_ring_ptr();
  if (iVar2 == 0) {
    uVar4 = 0;
  }
  else {
    uVar4 = (uint)*(ushort *)(iVar2 + 0x8500);
  }
  if (uVar4 == 0) {
    uVar3 = 0;
  }
  else {
    if (param_1 < 0) {
      param_1 = 0;
    }
    uVar6 = 0;
    uVar3 = 0;
    while (uVar5 = uVar4, (uVar6 & 0xffff) < uVar5) {
      uVar4 = uVar5 + (uVar6 & 0xffff) >> 1;
      if (*(int *)(iVar1 + uVar4 * 4 + 0xbc) <= param_1) {
        uVar6 = uVar4 + 1;
        uVar3 = uVar4;
        uVar4 = uVar5;
      }
    }
  }
  return uVar3;
}

