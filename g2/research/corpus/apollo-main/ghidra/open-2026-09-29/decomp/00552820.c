
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00552820(void)

{
  int *piVar1;
  
  *DAT_00552884 = 0;
  *_DAT_00552894 = 0;
  piVar1 = DAT_00552858;
  if (*DAT_00552858 != 0) {
    ui_common_api_fn_00509c96(*DAT_00552858);
    *piVar1 = 0;
  }
  FUN_0054ff48();
  *_DAT_005528ac = 0xff;
  *_DAT_005528b0 = 0xff;
  *_DAT_005528b4 = 0xff;
  return;
}

