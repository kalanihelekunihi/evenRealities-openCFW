
undefined8 FUN_0047de18(int param_1,undefined4 *param_2,int param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  int local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  uVar1 = FUN_0044a43c(param_1);
  if (((uVar1 < 8) || (iVar2 = FUN_0044b610(param_1,&DAT_0047e084,3), iVar2 != 0)) ||
     (iVar2 = FUN_0046cacc(param_1 + uVar1 + -4,DAT_0047e298), iVar2 != 0)) {
    uVar3 = 0;
  }
  else {
    local_18 = 0;
    uVar3 = FUN_0048d874(param_1 + 3,&local_18,10);
    if ((local_18 == 0) || (local_18 != param_1 + uVar1 + -4)) {
      uVar3 = 0;
    }
    else {
      *param_2 = uVar3;
      uVar3 = 1;
    }
  }
  return CONCAT44(local_18,uVar3);
}

