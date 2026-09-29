
undefined8 FUN_005cfe54(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
LAB_005cfe5a:
  do {
    iVar1 = FUN_005cfaf4(param_1,1,&local_10);
    if (iVar1 == 0) {
LAB_005cfea6:
      iVar1 = 0xa0;
      goto LAB_005cfea8;
    }
    iVar1 = FUN_005cfb62(iVar1,local_10);
    if (iVar1 - 0x14U < 2) {
      iVar1 = 0;
      goto LAB_005cfea8;
    }
    if (iVar1 - 0x32U < 2) {
      iVar1 = FUN_005cfd38(param_1);
    }
    else {
      if (iVar1 != 0x35) {
        if (iVar1 - 0x32U != 0x19) goto LAB_005cfea6;
        goto LAB_005cfe5a;
      }
      iVar1 = FUN_005cfc26(param_1);
    }
    if (iVar1 != 0) {
LAB_005cfea8:
      return CONCAT44(local_10,iVar1);
    }
  } while( true );
}

