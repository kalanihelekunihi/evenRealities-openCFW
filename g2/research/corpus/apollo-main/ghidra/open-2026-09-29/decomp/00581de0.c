
undefined4 FUN_00581de0(undefined1 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_34 [12];
  uint local_28;
  undefined1 auStack_20 [20];
  
  uVar1 = DAT_005827f0;
  if (param_1 == (undefined1 *)0x0) {
    FUN_004733ee(DAT_005827ec);
    uVar1 = 0xffffffff;
  }
  else {
    FUN_004905f4(auStack_20,DAT_005827f0,0xfb2);
    FUN_00439c04(auStack_34,auStack_20,0x14);
    iVar2 = FUN_00490c32(auStack_34,DAT_005827f4,param_1);
    if (iVar2 == 0) {
      FUN_004733ee(DAT_005827f8);
      uVar1 = 0xffffffff;
    }
    else {
      iVar2 = FUN_00464f76(0xb,uVar1,local_28 & 0xffff,0,0);
      if (iVar2 == 0) {
        FUN_004733ee(DAT_00582800,*param_1,param_1[1],local_28);
        uVar1 = 0;
      }
      else {
        FUN_004733ee(DAT_005827fc);
        uVar1 = 0xffffffff;
      }
    }
  }
  return uVar1;
}

