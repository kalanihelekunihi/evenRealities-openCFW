
void ui_onboarding_stock_sub_0050E728(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  for (iVar2 = 0; iVar3 = DAT_0050e928, iVar2 < 3; iVar2 = iVar2 + 1) {
    iVar3 = DAT_0050e928 + iVar2 * 0x60;
    *(undefined1 *)(iVar3 + 0x5c) = 0;
    *(undefined4 *)(iVar3 + 0x54) = 0;
    *(undefined4 *)(iVar3 + 0x58) = 0;
  }
  *(undefined1 *)(DAT_0050e928 + 0x124) = 0;
  *(undefined4 *)(iVar3 + 0x120) = 0;
  *DAT_0050e940 = 0;
  FUN_0043c0e4(DAT_0050e944,0x14,0);
  *DAT_0050e7e0 = 0;
  for (iVar2 = 0; iVar2 < 3; iVar2 = iVar2 + 1) {
    *(undefined4 *)(DAT_0050e94c + iVar2 * 4) = 0;
  }
  *DAT_0050e948 = 0;
  FUN_0043c0e4(DAT_0050e950,0x380,0);
  FUN_0043c0e4(DAT_0050e954,0x388,0);
  if (*DAT_0050e868 != 0) {
    *DAT_0050e868 = 0;
  }
  *DAT_0050e958 = 0;
  *DAT_0050e95c = 0;
  *DAT_0050e960 = 0;
  *DAT_0050e964 = 0;
  piVar1 = DAT_0050e968;
  if (*DAT_0050e968 != 0) {
    ui_common_api_fn_00509c96(*DAT_0050e968);
    *piVar1 = 0;
  }
  return;
}

