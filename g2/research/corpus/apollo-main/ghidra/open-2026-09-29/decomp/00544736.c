
undefined4
FUN_00544736(int param_1,int param_2,char param_3,undefined4 param_4,undefined4 param_5,
            code *param_6,char param_7)

{
  int iVar1;
  int iVar2;
  
  iVar1 = 0;
  iVar2 = *(int *)(param_1 + 0x14);
  do {
    iVar1 = *(int *)(param_1 + 0xc) + iVar1;
    FUN_0054418e(param_1,iVar2,param_2,0);
    if ((param_3 == '\0') || (param_3 == *(char *)(param_2 + 1))) {
      if (param_7 != '\0') {
        FUN_0054418e(param_1,iVar2,param_2,1);
      }
      if ((param_6 != (code *)0x0) && (iVar2 = (*param_6)(param_2,param_4,param_5), iVar2 != 0)) {
        return param_4;
      }
    }
    iVar2 = FUN_00544374(param_1,param_2,iVar1);
    if (iVar2 == -1) {
      return param_4;
    }
  } while( true );
}

