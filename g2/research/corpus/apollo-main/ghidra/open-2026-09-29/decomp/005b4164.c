
undefined8 FUN_005b4164(int param_1,short param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_005b486c;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x93;
      FUN_0043d574(2,DAT_005b485c,DAT_005b4858,DAT_005b4870);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__conversate_data_prep_note_layou_005b4874,
                          PTR_s__conversate_data_prep_note_layou_005b4874);
    }
  }
  else {
    FUN_005b4000(param_1,param_2);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

