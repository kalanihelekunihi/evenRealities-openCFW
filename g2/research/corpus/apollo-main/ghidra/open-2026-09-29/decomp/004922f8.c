
undefined4
SVC_KvdbReadLanguage(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  uint *puVar1;
  int iVar2;
  uint uStack_c;
  
  uStack_c = param_4;
  iVar2 = SVC_KvdbBlobRead(PTR_s_kvSystemLanguage_00492be8,&uStack_c,1,param_4,param_1,param_2,
                           param_3);
  if (0 < iVar2) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataLanguage_00492bf0,0x1d,
                   PTR_s_SVC_KvdbReadLanguage__language_i_00492bec,uStack_c & 0xff);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00492bfc,DAT_00492bfc,uStack_c & 0xff);
    }
    if ((uStack_c & 0xff) < 8) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataLanguage_00492bf0,0x1f,
                     PTR_s_SVC_KvdbReadLanguage__language_i_00492bec,uStack_c & 0xff);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00492bfc,DAT_00492bfc,uStack_c & 0xff);
      }
      *DAT_00492c00 = uStack_c & 0xff;
      return 0;
    }
  }
  puVar1 = DAT_00492c00;
  *DAT_00492c00 = 0;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataLanguage_00492bf0,0x25,DAT_00492c04,
                 *puVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_00492c08,DAT_00492c08,*puVar1);
  }
  return 0;
}

