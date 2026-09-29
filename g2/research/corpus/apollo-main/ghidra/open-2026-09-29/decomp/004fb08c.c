
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004fb08c(void)

{
  int *piVar1;
  undefined4 *puVar2;
  
  FUN_004f8348();
  piVar1 = DAT_004fb174;
  if (*DAT_004fb174 != 0) {
    ui_common_api_fn_00509c96(*DAT_004fb174);
    *piVar1 = 0;
  }
  *DAT_004fb178 = 0;
  *DAT_004fb17c = 0;
  *DAT_004fb14c = 0;
  *DAT_004fb190 = 0;
  *DAT_004fb160 = 0xffffffff;
  puVar2 = DAT_004fb194;
  *DAT_004fb194 = 0;
  puVar2[1] = 0;
  *DAT_004fb198 = 0;
  *DAT_004fb19c = 0;
  *_DAT_004fb1a0 = 0;
  return 0;
}

