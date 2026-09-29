
longlong settings_apply_auto_brightness(void)

{
  int iVar1;
  uint unaff_r7;
  
  iVar1 = FUN_00443484();
  if (iVar1 == 0) {
    iVar1 = FUN_0045a568();
    if (iVar1 == 1) {
      FUN_00466890();
    }
  }
  else {
    iVar1 = FUN_0047394c();
    (**(code **)(iVar1 + 0x14))(*(undefined1 *)(DAT_0046c6a8 + 1));
  }
  return (ulonglong)unaff_r7 << 0x20;
}

