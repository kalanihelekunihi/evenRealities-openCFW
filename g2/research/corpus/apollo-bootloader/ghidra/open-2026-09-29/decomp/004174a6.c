
void FUN_004174a6(byte param_1,undefined4 param_2)

{
  if (5 < param_1) {
    if (*DAT_00417be8 == 0) {
      elog_output(0,DAT_00417be4,DAT_00417be0,DAT_00417bfc,0x141,DAT_00417bf4,DAT_00417c00,
                  DAT_00417bfc,0x141);
      do {
        FUN_0041ac8a();
      } while( true );
    }
    (*(code *)*DAT_00417be8)(DAT_00417c00,DAT_00417bfc,0x141);
  }
  *(undefined4 *)(DAT_00417bcc + (uint)param_1 * 4 + 0xd8) = param_2;
  return;
}

