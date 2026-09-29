
undefined4 FUN_004b480a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = 0;
  FUN_0052e5ce(DAT_004b4d50,4,*DAT_004b4d4c);
  FUN_0052e5f2(*DAT_004b4d58,*DAT_004b4d54 & 0xff);
  do {
    bVar2 = bVar2 + 1;
    iVar1 = FUN_0052edf0(param_1,1);
    if (iVar1 == 0) {
      FUN_004733ee(DAT_004b4d5c);
      FUN_0052eefa(param_1,*DAT_004b4d60);
      FUN_0044b0ae();
      FUN_0052e4b4(param_1);
    }
    else {
      FUN_004733ee(DAT_004b4d64,iVar1);
      FUN_0052edd8(1);
    }
  } while ((bVar2 < 2) && (iVar1 != 0));
  return param_4;
}

