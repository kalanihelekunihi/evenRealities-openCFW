
undefined8 FUN_005ecb52(short param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_005ed744;
  if (param_1 == -1) {
    uVar2 = *(undefined4 *)(DAT_005ed744 + 0x248);
  }
  else {
    iVar3 = FUN_005eca64((int)param_1);
    if (iVar3 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = *(undefined4 *)(iVar1 + param_1 * 4 + 0x24c);
    }
  }
  return CONCAT44(param_4,uVar2);
}

