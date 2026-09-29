
undefined4 FUN_005bf298(undefined4 param_1,undefined4 param_2)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar2 = FUN_00499416();
  FUN_0043f4c0(uVar2,0x3fffffff);
  uVar3 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar2,uVar3,0);
  piVar1 = DAT_005bf8a8;
  FUN_0044143e(uVar2,*DAT_005bf8a8,0);
  FUN_0044144c(uVar2,0x1c - *(int *)(*piVar1 + 0xc),0);
  FUN_0044145a(uVar2,1,0);
  FUN_0049942e(uVar2,param_2);
  return uVar2;
}

