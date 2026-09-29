
void FUN_005443b0(int param_1,int param_2,undefined4 param_3,undefined4 param_4,code *param_5)

{
  int iVar1;
  int iVar2;
  undefined1 uStack_38;
  char local_37;
  int local_34;
  undefined4 uStack_20;
  
  iVar2 = 0;
  iVar1 = *(int *)(param_1 + 0x14);
  uStack_20 = param_4;
  do {
    iVar2 = *(int *)(param_1 + 0xc) + iVar2;
    iVar1 = FUN_0054418e(param_1,iVar1,&uStack_38,0);
    if (((iVar1 == 0) && (param_5 != (code *)0x0)) && ((local_37 == '\x02' || (local_37 == '\x03')))
       ) {
      *(int *)(param_2 + 0x50) = local_34 + 0x10;
      do {
        FUN_00544000(param_1,param_2);
        iVar1 = (*param_5)(param_2,param_3,param_4);
        if (iVar1 != 0) {
          return;
        }
        iVar1 = FUN_00543f8c(param_1,&uStack_38,param_2);
        *(int *)(param_2 + 0x50) = iVar1;
      } while (iVar1 != -1);
    }
    iVar1 = FUN_00544374(param_1,&uStack_38,iVar2);
  } while (iVar1 != -1);
  return;
}

