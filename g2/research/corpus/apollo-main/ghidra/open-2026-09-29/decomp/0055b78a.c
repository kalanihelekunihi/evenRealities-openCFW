
undefined2 FUN_0055b78a(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  undefined2 local_10 [2];
  undefined4 uStack_c;
  
  local_10[0] = 0;
  uStack_c = in_r3;
  iVar1 = FUN_0055b3a8(DAT_0055ba00,local_10);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0055b9d4,DAT_0055b9d0,DAT_0055ba24,0x179,DAT_0055ba2c,local_10[0],
                   local_10[0]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0055ba30,DAT_0055ba30,local_10[0],local_10[0]);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0055b9d4,DAT_0055b9d0,DAT_0055ba24,0x175,DAT_0055ba20,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0055ba28,DAT_0055ba28,iVar1);
    }
    local_10[0] = 0xffff;
  }
  return local_10[0];
}

