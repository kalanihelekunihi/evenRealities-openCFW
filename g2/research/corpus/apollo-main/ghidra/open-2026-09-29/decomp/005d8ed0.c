
int FUN_005d8ed0(int *param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = 0;
  iVar3 = *param_1;
LAB_005d8ee2:
  do {
    iVar3 = iVar3 + -1;
    iVar4 = iVar3;
    if (iVar3 < 1) {
      return iVar2;
    }
    do {
      iVar4 = iVar4 + -1;
      if (iVar4 < 0) goto LAB_005d8ee2;
      iVar1 = FUN_005d8db4(param_1,iVar3,iVar4);
    } while (iVar1 == 0);
    iVar2 = FUN_005d8e02(param_1,iVar4,iVar3,param_2);
    if (iVar2 != 0) {
      return iVar2;
    }
  } while( true );
}

