
undefined4 FUN_005ea810(ushort param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  
  iVar1 = DAT_005eb28c;
  iVar2 = td_ring_ptr();
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = *(ushort *)(iVar2 + 0x8500);
  }
  for (uVar4 = 0; uVar4 < 0xc; uVar4 = uVar4 + 1) {
    iVar2 = *(int *)(iVar1 + uVar4 * 4 + 0xc);
    if (iVar2 != 0) {
      if (uVar4 + param_1 < (uint)uVar3) {
        FUN_005ea768(uVar4,uVar4 + param_1 & 0xffff);
      }
      else {
        FUN_0043ded4(iVar2,1);
      }
    }
  }
  *(ushort *)(iVar1 + 0x1c0) = param_1;
  *(undefined1 *)(iVar1 + 0x1c2) = 1;
  return param_4;
}

