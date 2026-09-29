
undefined8 FUN_005ea8ce(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  ushort uVar4;
  
  iVar2 = td_ring_ptr();
  if (iVar2 == 0) {
    uVar4 = 0;
  }
  else {
    uVar4 = *(ushort *)(iVar2 + 0x8500);
  }
  if (uVar4 == 0) {
    uVar3 = 0;
  }
  else {
    uVar1 = FUN_005ea868(param_1);
    if (uVar1 < 3) {
      uVar1 = 0;
    }
    else {
      uVar1 = uVar1 - 2;
    }
    if (uVar4 < 0xd) {
      uVar4 = 0;
    }
    else {
      uVar4 = uVar4 - 0xc;
    }
    if (uVar4 < uVar1) {
      uVar1 = uVar4;
    }
    uVar3 = (uint)uVar1;
  }
  return CONCAT44(param_4,uVar3);
}

