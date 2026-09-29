
undefined8 FUN_004d0608(undefined4 param_1,uint param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_004d05fa();
  uVar2 = FUN_004cfeee(param_3 - iVar1,4);
  if ((param_2 & 3) == 0) {
    if ((uVar2 < *DAT_004d0854) || (*DAT_004d06e8 < uVar2)) {
      FUN_004733ee(DAT_004d099c,*DAT_004d0854 + iVar1,*DAT_004d06e8 + iVar1);
      param_2 = 0;
    }
    else {
      uVar3 = FUN_004cfe1a(param_2,-*DAT_004d0964);
      FUN_004cfd84(uVar3,uVar2);
      FUN_004cfdc0(uVar3);
      FUN_004cfdf6(uVar3);
      FUN_004d019a(param_1,uVar3);
      uVar3 = FUN_004cfe88(uVar3);
      FUN_004cfd84(uVar3,0);
      FUN_004cfdce(uVar3);
      FUN_004cfde8(uVar3);
    }
  }
  else {
    FUN_004733ee(DAT_004d0998,4);
    param_2 = 0;
  }
  return CONCAT44(param_4,param_2);
}

