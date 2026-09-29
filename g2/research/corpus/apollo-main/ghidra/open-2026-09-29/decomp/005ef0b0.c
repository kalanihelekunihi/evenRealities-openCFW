
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 tt_property_set(int param_1,undefined4 param_2,int *param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = FUN_0046cacc(param_2,_DAT_005efafc);
  if (iVar1 == 0) {
    iVar1 = *param_3;
    if ((iVar1 == 0x23) || (iVar1 == 0x28)) {
      *(int *)(param_1 + 0x40) = iVar1;
    }
    else {
      uVar2 = 7;
    }
  }
  else {
    uVar2 = 0xc;
  }
  return uVar2;
}

