
undefined8 FUN_0041715c(undefined4 param_1,uint param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0041714c();
  uVar2 = FUN_00416b7a(param_3 - iVar1,4);
  if ((param_2 & 3) == 0) {
    if ((uVar2 < *DAT_004172dc) || (*DAT_0041723c < uVar2)) {
      FUN_00415fae(DAT_0041732c,*DAT_004172dc + iVar1,*DAT_0041723c + iVar1);
      param_2 = 0;
    }
    else {
      uVar3 = FUN_00416aa6(param_2,-*DAT_00417308);
      FUN_00416a10(uVar3,uVar2);
      FUN_00416a4c(uVar3);
      FUN_00416a82(uVar3);
      FUN_00416e26(param_1,uVar3);
      uVar3 = FUN_00416b14(uVar3);
      FUN_00416a10(uVar3,0);
      FUN_00416a5a(uVar3);
      FUN_00416a74(uVar3);
    }
  }
  else {
    FUN_00415fae(DAT_00417328,4);
    param_2 = 0;
  }
  return CONCAT44(param_4,param_2);
}

