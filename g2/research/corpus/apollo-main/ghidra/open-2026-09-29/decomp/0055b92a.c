
undefined8 FUN_0055b92a(undefined2 *param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0055b530(DAT_0055ba00,param_1);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x19a;
      FUN_0043d574(3,DAT_0055b9d4,DAT_0055b9d0,DAT_0055ba54,0x19a,DAT_0055ba5c,*param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0055ba60,DAT_0055ba60,*param_1);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x196;
      FUN_0043d574(1,DAT_0055b9d4,DAT_0055b9d0,DAT_0055ba54,0x196,DAT_0055ba50,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0055ba58,DAT_0055ba58,iVar1);
    }
    uVar3 = 0xffffffff;
  }
  return CONCAT44(param_2,uVar3);
}

