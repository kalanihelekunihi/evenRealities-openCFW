
int FUN_10004340(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4,
                undefined4 param_5)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = FUN_10004020();
  piVar1 = DAT_10004384;
  if (iVar2 != -1) {
    iVar2 = *DAT_10004384;
    iVar3 = 0x101 << (param_4 & 0x3f);
    *(int *)(iVar2 + 0x310) = iVar3;
    FUN_10003274(piVar1[param_4 + 0xda],0x1a0,param_3,iVar2,param_5);
    iVar2 = 0;
    *(int *)(*piVar1 + 0x3a0) = iVar3;
  }
  return iVar2;
}

