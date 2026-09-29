
void FUN_0043d33c(byte param_1,undefined4 param_2)

{
  if (5 < param_1) {
    if (*DAT_0043daa0 == 0) {
      FUN_0043d574(0,PTR_DAT_0043da8c,DAT_0043da88,DAT_0043dab4,0x141,DAT_0043daac,DAT_0043dab8,
                   DAT_0043dab4,0x141);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0043daa0)(DAT_0043dab8,DAT_0043dab4,0x141);
  }
  *(undefined4 *)(DAT_0043da70 + (uint)param_1 * 4 + 0xd8) = param_2;
  return;
}

