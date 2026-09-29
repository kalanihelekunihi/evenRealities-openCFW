
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00554c68(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  
  uVar1 = FUN_0043de82();
  iVar2 = func_0x005540f0();
  FUN_0043f4c0(uVar1,2,iVar2 * 0x1c);
  FUN_0044146a(uVar1,6,0);
  uVar3 = FUN_0044104c(_DAT_005558bc);
  FUN_0044127e(uVar1,uVar3,0);
  FUN_0044129e(uVar1,0x7f,0);
  FUN_0044131c(uVar1,0,0);
  FUN_00554080(uVar1,0,0);
  FUN_0043dfa4(uVar1,0x10);
  uVar3 = FUN_0043de82(uVar1);
  FUN_0043f4c0(uVar3,2,0x14);
  FUN_0044146a(uVar3,6,0);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044127e(uVar3,uVar4,0);
  FUN_0044129e(uVar3,0xff,0);
  FUN_0044131c(uVar3,0,0);
  FUN_00554080(uVar3,0,0);
  FUN_0043dfa4(uVar3,0x10);
  FUN_0043f6b8(uVar3,2,0,0);
  return CONCAT44(in_r3,uVar1);
}

