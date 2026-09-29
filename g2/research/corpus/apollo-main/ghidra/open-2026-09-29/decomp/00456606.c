
undefined8 FUN_00456606(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int local_20;
  
  uVar2 = DAT_00456bb4;
  uVar1 = DAT_00456bb0;
  local_20 = param_4;
  if (param_1 == 0) {
    uVar3 = 0;
  }
  else {
    iVar4 = FUN_0046cacc(param_1,PTR_s__log_hardfault_txt_00456bb8);
    if (iVar4 == 0) {
      uVar3 = 1;
    }
    else {
      uVar3 = FUN_0044a43c(param_1);
      iVar4 = FUN_0044a43c(uVar2);
      iVar5 = FUN_0044a43c(uVar1);
      if ((((uint)(iVar5 + iVar4) < uVar3) &&
          (iVar6 = FUN_0044b610(param_1,uVar2,iVar4), iVar6 == 0)) &&
         (iVar6 = FUN_0046cacc((param_1 + uVar3) - iVar5,uVar1), iVar6 == 0)) {
        local_20 = 0;
        FUN_0048d874(param_1 + iVar4,&local_20,10);
        uVar3 = (uint)(local_20 == (param_1 + uVar3) - iVar5);
      }
      else {
        uVar3 = 0;
      }
    }
  }
  return CONCAT44(local_20,uVar3);
}

