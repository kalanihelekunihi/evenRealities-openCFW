
longlong hub_msg_send_id3(void)

{
  undefined4 uVar1;
  
  uVar1 = *(undefined4 *)PTR_DAT_004a7384;
  HUB_SendMessage(&stack0xfffffff0);
  return (ulonglong)CONCAT22((short)((uint)uVar1 >> 0x10),3) << 0x20;
}

