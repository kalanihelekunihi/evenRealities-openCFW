
undefined4 FUN_0052e8be(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_28;
  undefined4 local_24;
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  local_24 = 0;
  uStack_10 = param_4;
  FUN_0048949c(auStack_20,0x10);
  local_28 = *DAT_0052f220;
  FUN_004733ee(DAT_0052f224);
  FUN_0052e8a4();
  do {
    while( true ) {
      do {
        FUN_0052e854(0x28);
      } while (-1 < *DAT_0052eba4 << 10);
      iVar1 = FUN_0052e1ea(param_1,auStack_20,&local_24);
      if (iVar1 == 0) break;
      FUN_004733ee(DAT_0052f228,iVar1);
      FUN_0052e8a4();
    }
    iVar1 = FUN_004751c8(auStack_20,&local_28,4);
  } while (iVar1 != 0);
  FUN_004733ee(DAT_0052f22c);
  return 0;
}

