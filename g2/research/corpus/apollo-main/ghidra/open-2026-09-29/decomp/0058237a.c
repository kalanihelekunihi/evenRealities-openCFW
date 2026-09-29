
undefined4 FUN_0058237a(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_34 [12];
  uint local_28;
  undefined1 auStack_20 [20];
  
  uVar1 = DAT_00582880;
  if (param_1 == 0) {
    FUN_004733ee(DAT_0058287c);
    uVar1 = 0xffffffff;
  }
  else {
    FUN_004905f4(auStack_20,DAT_00582880,0xfa9);
    FUN_00439c04(auStack_34,auStack_20,0x14);
    iVar2 = FUN_00490c32(auStack_34,DAT_00582884,param_1);
    if (iVar2 == 0) {
      FUN_004733ee(DAT_00582888);
      uVar1 = 0xffffffff;
    }
    else {
      iVar2 = FUN_00464f76(6,uVar1,local_28 & 0xffff,0,0);
      if (iVar2 == 0) {
        uVar1 = 0;
      }
      else {
        FUN_004733ee(DAT_0058288c);
        uVar1 = 0xffffffff;
      }
    }
  }
  return uVar1;
}

