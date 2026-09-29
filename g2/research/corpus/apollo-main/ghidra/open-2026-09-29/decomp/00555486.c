
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00555486(void)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  
  uVar2 = FUN_00499416();
  FUN_0043f4c0(uVar2,0x3fffffff,0x118);
  func_0x00499790(uVar2,0);
  uVar3 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar2,uVar3,0);
  uVar3 = FUN_0044104c(_DAT_005558bc);
  FUN_0044140e(uVar2,uVar3,0x40000);
  uVar3 = FUN_0044104c(0);
  FUN_0044127e(uVar2,uVar3,0x40000);
  piVar1 = _DAT_00556128;
  FUN_0044143e(uVar2,*_DAT_00556128,0);
  FUN_0044144c(uVar2,0x1c - *(int *)(*piVar1 + 0xc),0);
  FUN_0044145a(uVar2,1,0);
  FUN_0049942e(uVar2,&DAT_00555748);
  return CONCAT44(in_r3,uVar2);
}

