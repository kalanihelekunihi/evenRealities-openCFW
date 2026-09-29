
undefined4 FUN_004faf20(void)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 in_r3;
  
  FUN_004f8348();
  FUN_004f8298();
  puVar1 = DAT_004fb170;
  iVar3 = FUN_0044ddea(*DAT_004fb170);
  while (piVar2 = DAT_004fb174, iVar3 = iVar3 + -1, -1 < iVar3) {
    iVar4 = FUN_0044dce2(*puVar1,iVar3);
    if (iVar4 != 0) {
      FUN_0044d7b8();
    }
  }
  if (*DAT_004fb174 != 0) {
    ui_common_api_fn_00509c96(*DAT_004fb174);
    *piVar2 = 0;
  }
  *DAT_004fb178 = 0;
  *DAT_004fb17c = 0;
  FUN_004f8644(0,0);
  FUN_004e92f4();
  FUN_005000cc(*DAT_004fb180,4);
  return in_r3;
}

