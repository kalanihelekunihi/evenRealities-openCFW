
undefined8 FUN_004761d2(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = DAT_00476474;
  FUN_004cfa6c(DAT_00476474);
  uVar1 = DAT_00476490;
  FUN_004cfa58(uVar4,DAT_00476490);
  iVar2 = FUN_004cfa62(uVar4,uVar1);
  if (iVar2 == 0) {
    iVar2 = FUN_00475fe8();
    if (iVar2 == 0) {
      uVar4 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x6f;
        FUN_0043d574(2,DAT_00476464,DAT_00476460,DAT_00476498,0x6f,DAT_004764a0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004764a4);
      }
      uVar4 = 9;
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x6b;
      FUN_0043d574(2,DAT_00476464,DAT_00476460,DAT_00476498,0x6b,DAT_00476494,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0047649c,DAT_0047649c,iVar2);
    }
    uVar4 = 9;
  }
  return CONCAT44(param_2,uVar4);
}

