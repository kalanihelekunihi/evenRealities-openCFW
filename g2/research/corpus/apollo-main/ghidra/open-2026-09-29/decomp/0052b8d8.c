
undefined8
WsfSetOsSpecificEvent(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int local_10;
  undefined4 uStack_c;
  
  piVar1 = DAT_0052babc;
  local_10 = param_3;
  uStack_c = param_4;
  if (*DAT_0052babc != 0) {
    iVar2 = FUN_00442228();
    if (iVar2 == 1) {
      local_10 = 0;
      iVar2 = FUN_0047ee4a(*piVar1,1,&local_10);
      if ((iVar2 != 0) && (local_10 != 0)) {
        *DAT_0052bac0 = 0x10000000;
      }
    }
    else {
      iVar2 = FUN_0047ed76(*piVar1,1);
      if (iVar2 != 0) {
        FUN_004420bc();
      }
    }
  }
  return CONCAT44(uStack_c,local_10);
}

