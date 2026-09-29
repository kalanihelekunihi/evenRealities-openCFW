
void conversate_ui_menu_input_handler(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_005b43e8(0);
  if (param_1 == 0x48) {
    system_close_page_factory_0046ae9c(1,0xb);
  }
  else if (param_1 == 10) {
    conversate_ui_send_start_request();
    FUN_005b02e4(0xc,0);
  }
  else if (param_1 == 0x44) {
    iVar2 = FUN_005b5752(DAT_005b5cc8,uVar1);
    if (iVar2 != 0) {
      FUN_005b02e4(0xe,iVar2);
    }
  }
  else if ((param_1 == 0x45) && (iVar2 = FUN_005b577c(DAT_005b5cc8,uVar1), iVar2 != 0)) {
    FUN_005b02e4(0xf,iVar2);
  }
  return;
}

