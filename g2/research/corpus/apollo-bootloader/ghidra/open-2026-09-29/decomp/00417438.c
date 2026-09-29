
void FUN_00417438(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if ((param_1 != '\0') && (param_1 != '\x01')) {
    if (*DAT_00417be8 == 0) {
      elog_output(0,DAT_00417be4,DAT_00417be0,DAT_00417bf8,0x122,DAT_00417bf4,DAT_00417bf0,
                  DAT_00417bf8,0x122,param_4);
      do {
        FUN_0041ac8a();
      } while( true );
    }
    (*(code *)*DAT_00417be8)(DAT_00417bf0,DAT_00417bf8,0x122);
  }
  *(char *)(DAT_00417bcc + 0xf5) = param_1;
  return;
}

