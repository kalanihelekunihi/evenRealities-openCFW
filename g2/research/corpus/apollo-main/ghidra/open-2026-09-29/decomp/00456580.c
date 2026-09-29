
undefined8 FUN_00456580(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  byte bVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int local_20;
  
  uVar2 = DAT_00456bb0;
  uVar1 = DAT_00456bac;
  local_20 = param_4;
  iVar4 = FUN_0044a43c(DAT_00456bac);
  iVar5 = FUN_0044a43c(uVar2);
  if (param_1 == 0) {
    uVar6 = 0;
  }
  else {
    uVar6 = FUN_0044a43c(param_1);
    if ((((uint)(iVar5 + iVar4) < uVar6) && (iVar7 = FUN_0044b610(param_1,uVar1,iVar4), iVar7 == 0))
       && (iVar7 = FUN_0046cacc((param_1 + uVar6) - iVar5,uVar2), iVar7 == 0)) {
      local_20 = 0;
      iVar4 = FUN_0048d874(param_1 + iVar4,&local_20,10);
      if ((iVar4 == 0) || (local_20 != (param_1 + uVar6) - iVar5)) {
        bVar3 = 0;
      }
      else {
        bVar3 = 1;
      }
      uVar6 = (uint)bVar3;
    }
    else {
      uVar6 = 0;
    }
  }
  return CONCAT44(local_20,uVar6);
}

