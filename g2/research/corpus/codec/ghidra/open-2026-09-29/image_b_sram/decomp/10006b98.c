
undefined4 FUN_10006b98(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*DAT_10006bc4 == 0) {
    FUN_10009934(PTR_s__AOUT_ERROR___s__d_10006bcc,PTR_s_gx_audio_out_set_db_10006bc8,0x145);
    return 0xffffffff;
  }
  uVar2 = *(uint *)(*DAT_10006bc4 + 0x38);
  if (uVar2 != 0) {
    uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    return uVar1;
  }
  return 0;
}

