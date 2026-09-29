
undefined8
tt_check_trickyness_family
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    if (0x19 < iVar3) {
      uVar2 = 0;
LAB_005f8542:
      return CONCAT44(param_4,uVar2);
    }
    iVar1 = FUN_0044b63a(param_1,iVar3 * 0x14 + DAT_005f9194);
    if (iVar1 != 0) {
      uVar2 = 1;
      goto LAB_005f8542;
    }
    iVar3 = iVar3 + 1;
  } while( true );
}

