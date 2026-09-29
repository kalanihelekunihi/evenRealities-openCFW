
int FUN_00596b0c(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  code *pcVar4;
  
  if (param_1 < 7) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = FUN_00596b00(param_1);
      FUN_0043d574(3,DAT_00597028,DAT_00597024,DAT_00597020,0x57,DAT_00597030,param_1,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = FUN_00596b00(param_1);
      compress_log_output(0xc800000,DAT_00597034,DAT_00597034,param_1,uVar2);
    }
    pcVar4 = *(code **)(DAT_00597038 + (uint)param_1 * 4);
    if (pcVar4 == (code *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = FUN_00596b00(param_1);
        FUN_0043d574(2,DAT_00597028,DAT_00597024,DAT_00597020,0x5e,DAT_0059703c,param_1,uVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        uVar2 = FUN_00596b00(param_1);
        compress_log_output(0x8800000,DAT_00597040,DAT_00597040,param_1,uVar2);
      }
      iVar1 = -1;
    }
    else {
      iVar1 = (*pcVar4)(DAT_00597044,param_2,param_3);
      if (iVar1 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00597028,DAT_00597024,DAT_00597020,0x65,DAT_00597048);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0059704c,DAT_0059704c);
        }
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00597028,DAT_00597024,DAT_00597020,0x53,DAT_0059701c,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0059702c,DAT_0059702c);
    }
    iVar1 = -1;
  }
  return iVar1;
}

