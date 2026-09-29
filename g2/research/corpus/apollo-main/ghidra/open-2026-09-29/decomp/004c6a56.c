
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 device_mgr_fn_004c6a56(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  if (*_DAT_004c6c84 == '\0') {
    aud_send_message_type1(0);
    iVar1 = FUN_0045a568();
    if (iVar1 == 2) {
      aud_send_message_type0(1);
    }
    FUN_004442d0(0x104,0,0);
    DRV_BuzzerPlay(0);
  }
  else {
    aud_send_message_type1(1);
    iVar1 = FUN_0045a568();
    if (iVar1 == 2) {
      aud_send_message_type0(0);
    }
  }
  return unaff_r7;
}

