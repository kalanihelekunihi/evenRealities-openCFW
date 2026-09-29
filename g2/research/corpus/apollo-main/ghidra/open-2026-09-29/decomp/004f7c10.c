
undefined4 FUN_004f7c10(int param_1)

{
  char *pcVar1;
  undefined4 unaff_r7;
  
  pcVar1 = DAT_004f81d8;
  if (((*DAT_004f8094 != 0) && (*DAT_004f7f14 == 0)) && (*DAT_004f81d8 == '\x02')) {
    *DAT_004f7f14 = 1;
    *pcVar1 = '\x04';
    if (param_1 < (int)(uint)*DAT_004f7c90) {
      if (param_1 < 0) {
        *DAT_004f81e4 = -2;
        FUN_004f7634(0,100,DAT_004f8624);
      }
      else {
        *DAT_004f81e4 = param_1;
        FUN_004f7634(0,100,DAT_004f88a4);
      }
    }
    else {
      *DAT_004f81e4 = -1;
      FUN_004f7634(0,100,DAT_004f8624);
    }
  }
  return unaff_r7;
}

