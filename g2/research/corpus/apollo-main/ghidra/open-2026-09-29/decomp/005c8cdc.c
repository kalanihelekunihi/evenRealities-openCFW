
undefined4 FUN_005c8cdc(undefined4 param_1,undefined4 param_2)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  
  piVar1 = DAT_005c8fdc;
  *DAT_005c8fdc = 0;
  FUN_00451670(param_1,0x24,param_2);
  if ((*piVar1 == 0) || (*(char *)*piVar1 != '\0')) {
    if ((*piVar1 == 0) || (iVar3 = FUN_004547be(*piVar1,param_2), iVar3 == 0)) {
      uVar2 = 1;
    }
    else {
      FUN_005c7a60(param_1,*piVar1);
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

