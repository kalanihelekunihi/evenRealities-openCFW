
undefined8 FUN_005b577c(int param_1,ushort *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((param_2 == (ushort *)0x0) || (*param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_005897e0();
    if ((iVar2 == 0) && (*(int *)(param_1 + 0x84) < (int)(*param_2 - 1))) {
      uVar1 = 1;
    }
    else {
      uVar1 = 0;
    }
  }
  return CONCAT44(param_4,uVar1);
}

