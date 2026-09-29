
void FUN_0043d2ce(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if ((param_1 != '\0') && (param_1 != '\x01')) {
    if (*DAT_0043daa0 == 0) {
      FUN_0043d574(0,PTR_DAT_0043da8c,DAT_0043da88,DAT_0043dab0,0x122,DAT_0043daac,DAT_0043daa8,
                   DAT_0043dab0,0x122,param_4);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0043daa0)(DAT_0043daa8,DAT_0043dab0,0x122);
  }
  *(char *)(DAT_0043da70 + 0xf5) = param_1;
  return;
}

