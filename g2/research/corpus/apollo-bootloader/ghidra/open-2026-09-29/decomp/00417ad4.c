
bool get_fmt_enabled(byte param_1,uint param_2)

{
  if (5 < param_1) {
    if (*DAT_00417be8 == 0) {
      elog_output(0,DAT_00417be4,DAT_00417be0,DAT_00417c24,0x2e7,DAT_00417bf4,DAT_00417c00,
                  DAT_00417c24,0x2e7);
      do {
        FUN_0041ac8a();
      } while( true );
    }
    (*(code *)*DAT_00417be8)(DAT_00417c00,DAT_00417c24,0x2e7);
  }
  return (*(uint *)(DAT_00417bcc + (uint)param_1 * 4 + 0xd8) & param_2) != 0;
}

