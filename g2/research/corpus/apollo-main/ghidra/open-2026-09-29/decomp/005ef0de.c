
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 tt_property_get(int param_1,undefined4 param_2,undefined4 *param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = *(undefined4 *)(param_1 + 0x40);
  iVar1 = FUN_0046cacc(param_2,_DAT_005efafc);
  if (iVar1 == 0) {
    *param_3 = uVar2;
    uVar2 = 0;
  }
  else {
    uVar2 = 0xc;
  }
  return uVar2;
}

