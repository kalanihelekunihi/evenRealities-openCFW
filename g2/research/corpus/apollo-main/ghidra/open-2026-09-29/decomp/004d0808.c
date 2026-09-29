
undefined4 FUN_004d0808(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 != 0) {
    uVar1 = FUN_004cfe04(param_2);
    iVar2 = FUN_004cfdb4(uVar1);
    if (iVar2 != 0) {
      FUN_004d09b4(DAT_004d09b0,DAT_004d09a0,0x4a4);
    }
    FUN_004cfe96(uVar1);
    uVar1 = FUN_004d02d6(param_1,uVar1);
    uVar1 = FUN_004d033a(param_1,uVar1);
    FUN_004d019a(param_1,uVar1);
  }
  return param_4;
}

