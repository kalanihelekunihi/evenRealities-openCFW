
longlong FUN_005e576c(void)

{
  undefined1 uVar1;
  char cVar2;
  undefined4 uVar3;
  uint unaff_r7;
  
  func_0x005eae94();
  uVar1 = UX_GetSystemBLEStatus();
  cVar2 = FUN_005e50ea(uVar1);
  if (((cVar2 == '\x02') || (cVar2 == '\x03')) || (cVar2 == '\x04')) {
    terminal_request_display(cVar2,0);
  }
  else if (cVar2 == '\x16') {
    terminal_request_display(0x16,*(undefined4 *)(DAT_005e5dd8 + 0x288));
  }
  else {
    uVar3 = FUN_005ecafa();
    terminal_request_display(0x1b,uVar3);
  }
  return (ulonglong)unaff_r7 << 0x20;
}

