
void FUN_00417510(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (5 < param_1) {
    if (*DAT_00417be8 == 0) {
      elog_output(0,DAT_00417be4,DAT_00417be0,DAT_00417c04,0x15b,DAT_00417bf4,DAT_00417c00,
                  DAT_00417c04,0x15b,param_4);
      do {
        FUN_0041ac8a();
      } while( true );
    }
    (*(code *)*DAT_00417be8)(DAT_00417c00,DAT_00417c04,0x15b);
  }
  *DAT_00417bcc = param_1;
  return;
}

