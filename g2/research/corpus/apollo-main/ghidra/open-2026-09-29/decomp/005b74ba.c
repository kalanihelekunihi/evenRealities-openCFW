
undefined8 FUN_005b74ba(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  
  if (*(int *)(DAT_005b7604 + 0x1c) == 0) {
    uVar1 = 0xffffffff;
  }
  else if (*(char *)(DAT_005b7604 + 0x98) == '\0') {
    uVar1 = FUN_005b6cd0(0);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x1d5;
      FUN_0043d574(3,PTR_s_conversate_prep_005b7614,DAT_005b7610,
                   PTR_s_conversate_ui_action_prep_note_c_005b7678,0x1d5,
                   PTR_s_prep_note_content_ready_while_an_005b7674);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__conversate_prep_prep_note_conte_005b767c,
                          PTR_s__conversate_prep_prep_note_conte_005b767c);
    }
    uVar1 = 0;
  }
  return CONCAT44(unaff_r5,uVar1);
}

