
undefined8 FUN_00430610(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int local_10;
  undefined4 uStack_c;
  
  iVar1 = DAT_00430640;
  local_10 = param_3;
  uStack_c = param_4;
  iVar2 = hw_interrupt_status_get_42c672(*(undefined4 *)(DAT_00430640 + 0x44),1,&local_10);
  if ((iVar2 == 0) && (local_10 != 0)) {
    hw_interrupt_clear_42c6b6(*(undefined4 *)(iVar1 + 0x44),local_10);
    hw_event_service_42c6f8(*(undefined4 *)(iVar1 + 0x44),local_10);
  }
  return CONCAT44(uStack_c,local_10);
}

