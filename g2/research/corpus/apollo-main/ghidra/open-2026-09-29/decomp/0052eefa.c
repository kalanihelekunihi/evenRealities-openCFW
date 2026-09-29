
int FUN_0052eefa(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_110 [248];
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  uStack_18 = param_1;
  uStack_14 = param_2;
  FUN_0043c0e4(auStack_110,0xf8,0);
  uVar1 = DAT_0052f298;
  iVar2 = FUN_0052ea28(param_1,DAT_0052f298,auStack_110,0xf8);
  if (iVar2 == 0) {
    iVar2 = FUN_0052e948(param_1,1,1);
    if (iVar2 == 0) {
      FUN_00439be4(auStack_110,&uStack_14,4);
      iVar2 = FUN_0052eaf8(param_1,uVar1,auStack_110,0xf8);
      if (iVar2 != 0) {
        FUN_004733ee(DAT_0052f29c,iVar2);
      }
    }
    else {
      FUN_004733ee(DAT_0052f2a0,iVar2);
    }
  }
  else {
    FUN_004733ee(DAT_0052f2a4,iVar2);
  }
  return iVar2;
}

