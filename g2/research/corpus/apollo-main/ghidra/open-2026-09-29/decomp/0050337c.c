
undefined8 AppScanStart(undefined1 param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  uint local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_2;
  iVar1 = appMasterScanMode();
  if (iVar1 != 0) {
    FUN_0055bb68(1,*DAT_00503480,*DAT_00503480 + 2);
    local_14 = 0;
    local_18 = param_3 & 0xffff;
    FUN_0055baae(1,param_1,&uStack_10,1);
  }
  return CONCAT44(local_14,local_18);
}

