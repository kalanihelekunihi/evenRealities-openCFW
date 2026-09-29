
undefined8 hub_msg_send_id8(void)

{
  undefined4 uVar1;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  uVar1 = *(undefined4 *)(PTR_DAT_004a735c + 4);
  uStack_e = (undefined2)((uint)*(undefined4 *)PTR_DAT_004a735c >> 0x10);
  uStack_10 = 8;
  HUB_SendMessage(&uStack_10);
  return CONCAT44(uVar1,CONCAT22(uStack_e,uStack_10));
}

