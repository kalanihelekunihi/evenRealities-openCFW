
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00462ea8(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = FUN_00498668();
  if (*(int *)(DAT_00463014 + param_2 * 0x34) == 0) {
    FUN_0043f506(uVar1,0x14);
    FUN_0043f568(uVar1,0x14);
    uVar2 = FUN_0044104c(_DAT_00463b90);
    FUN_0044127e(uVar1,uVar2,0);
    FUN_0044129e(uVar1,0xff,0);
    FUN_0044146a(uVar1,4,0);
  }
  else {
    FUN_00498680(uVar1,*(undefined4 *)(DAT_00463014 + param_2 * 0x34));
    FUN_0043f0e0(uVar1,0x10);
    FUN_0043f142(uVar1,0xc);
    FUN_004413ce(uVar1,0x20,0);
  }
  return CONCAT44(param_4,uVar1);
}

