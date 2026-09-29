
undefined8 FUN_004f7480(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = *DAT_004f7c0c;
    uVar2 = 0x8bc;
    param_2 = DAT_004f7f04;
    FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f7f08,0x8bc,DAT_004f7f04,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004f7f0c,DAT_004f7f0c,*DAT_004f7c0c,uVar2,param_2,param_3);
  }
  if (*DAT_004f7c0c == 0) {
    FUN_004f7860(param_1);
  }
  else {
    FUN_004f6e6c(*DAT_004f8090,*DAT_004f7c0c,100,DAT_004f7f10);
  }
  return CONCAT44(param_2,uVar2);
}

