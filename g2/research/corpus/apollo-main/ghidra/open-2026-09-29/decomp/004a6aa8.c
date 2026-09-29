
longlong hub_msg_send_id4(void)

{
  undefined4 uVar1;
  
  uVar1 = *(undefined4 *)PTR_DAT_004a7380;
  HUB_SendMessage(&stack0xfffffff0);
  return (ulonglong)CONCAT22((short)((uint)uVar1 >> 0x10),4) << 0x20;
}

