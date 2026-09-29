
void FUN_004e8370(void)

{
  int *piVar1;
  int iVar2;
  
  *DAT_004e83bc = 0;
  *DAT_004e8bb8 = 0;
  *DAT_004e8db0 = *DAT_004e8dac;
  FUN_0043ded4(*DAT_004e8db4,1);
  piVar1 = DAT_004e8430;
  if ((*DAT_004e8430 != 0) && (iVar2 = ui_common_api_fn_00509dfa(*DAT_004e8430), iVar2 == 0)) {
    ui_common_api_fn_00509f52(*piVar1);
  }
  return;
}

