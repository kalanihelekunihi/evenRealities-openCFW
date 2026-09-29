
undefined8 FUN_00551814(int param_1,uint param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if ((param_1 == 0) || (param_3 == (int *)0x0)) {
    iVar1 = FUN_0043d0ce();
    uVar3 = param_2;
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x6c0;
      FUN_0043d574(1,DAT_0055221c,DAT_00552218,PTR_s_msg_notif_create_msg_item_00552240,0x6c0,
                   PTR_s_tileview_or_msg_item_is_NULL_0055223c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__message_notify_list_ui_tileview_00552244,
                          PTR_s__message_notify_list_ui_tileview_00552244);
    }
    param_3 = (int *)0x0;
  }
  else {
    uVar3 = param_2;
    FUN_0043c0e4(param_3,0x28,0,param_4,param_2,param_3,param_4);
    iVar1 = FUN_0050ff0e(param_1,0,param_2 & 0xff,0xc);
    *param_3 = iVar1;
    if (*param_3 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0x6ca;
        FUN_0043d574(1,DAT_0055221c,DAT_00552218,PTR_s_msg_notif_create_msg_item_00552240,0x6ca,
                     PTR_s_failed_to_create_message_object___00552248,param_2 & 0xff);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__message_notify_list_ui_failed_t_0055224c,
                            PTR_s__message_notify_list_ui_failed_t_0055224c,param_2 & 0xff);
      }
      param_3 = (int *)0x0;
    }
    else {
      FUN_0043f506(*param_3,0x224);
      FUN_0043f568(*param_3,0xd6);
      if ((param_2 & 0xff) == 0) {
        FUN_0043f6b8(*param_3,1,0,0);
      }
      else {
        iVar1 = FUN_0044dce2(param_1,(param_2 & 0xff) - 1);
        if (iVar1 == 0) {
          FUN_0043f6b8(*param_3,1,0,0);
        }
        else {
          uVar3 = 0;
          FUN_0043f6d6(*param_3,iVar1,0xd,0);
        }
      }
      FUN_0044131c(*param_3,0,0);
      FUN_0044146a(*param_3,0,0);
      uVar2 = FUN_0044104c(0);
      FUN_0044127e(*param_3,uVar2,0);
      FUN_0044129e(*param_3,0xff,0);
      FUN_0054fa24(*param_3,0,0);
      FUN_0044120e(*param_3,0x10,0);
      FUN_0043dfa4(*param_3,0x12);
      iVar1 = FUN_0043de82(*param_3);
      param_3[1] = iVar1;
      FUN_0043f506(param_3[1],0x224);
      FUN_0043f568(param_3[1],0x3fffffff);
      FUN_004411aa(param_3[1],0xc6,0);
      FUN_0043f6b8(param_3[1],9,0,0);
      FUN_0044131c(param_3[1],1,0);
      uVar2 = FUN_0044104c(0xffffff);
      FUN_004412ec(param_3[1],uVar2,0);
      FUN_0044146a(param_3[1],6,0);
      uVar2 = FUN_0044104c(0);
      FUN_0044127e(param_3[1],uVar2,0);
      FUN_0044129e(param_3[1],0xff,0);
      FUN_0054fa24(param_3[1],0x10,0);
      FUN_00441238(param_3[1],0xd,0);
      FUN_0043dfa4(param_3[1],0x12);
      iVar1 = FUN_00498668(param_3[1]);
      param_3[2] = iVar1;
      FUN_0043f4c0(param_3[2],0x1e,0x1e);
      FUN_00498680(param_3[2],PTR_DAT_00552250);
      FUN_0043f6b8(param_3[2],1,0,0);
      iVar1 = FUN_005514f0(param_3[1],param_3 + 3);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar3 = 0x6fd;
          FUN_0043d574(1,DAT_0055221c,DAT_00552218,PTR_s_msg_notif_create_msg_item_00552240,0x6fd,
                       PTR_s_failed_to_create_content_object_f_00552254,param_2 & 0xff);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__message_notify_list_ui_failed_t_00552258,
                              PTR_s__message_notify_list_ui_failed_t_00552258,param_2 & 0xff);
        }
        FUN_0044d7b8(*param_3);
        param_3 = (int *)0x0;
      }
    }
  }
  return CONCAT44(uVar3,param_3);
}

