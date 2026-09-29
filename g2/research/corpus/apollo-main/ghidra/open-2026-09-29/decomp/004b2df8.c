
void dmDevActReset(void)

{
  byte bVar1;
  
  if (*(char *)(DAT_004b306c + 0x10) == '\0') {
    *(undefined1 *)(DAT_004b306c + 0x10) = 1;
    for (bVar1 = 0; bVar1 < 0x15; bVar1 = bVar1 + 1) {
      (*(code *)**(undefined4 **)(DAT_004b3070 + (uint)bVar1 * 4))();
    }
    HciResetSequence();
  }
  return;
}

