
void case_configure_platform_routes(void)

{
  int iVar1;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  uint local_1c;
  
  FUN_080001e6(&local_30,0x14);
  iVar1 = DAT_08006b6c;
  *(uint *)(DAT_08006b6c + 0x34) = *(uint *)(DAT_08006b6c + 0x34) | 2;
  *(uint *)(iVar1 + 0x34) = *(uint *)(iVar1 + 0x34) | 4;
  *(uint *)(iVar1 + 0x34) = *(uint *)(iVar1 + 0x34) | 1;
  local_1c = *(uint *)(iVar1 + 0x34) & 1;
  case_register_write_channel(0x50000000,0xca,0);
  case_register_write_channel(DAT_08006b70,4,0);
  local_30 = DAT_08006b74;
  local_2c = 3;
  local_28 = 0;
  FUN_08004d30(DAT_08006b78,&local_30);
  local_2c = 0x210000;
  local_30 = 1;
  local_28 = 0;
  FUN_08004d30(0x50000000,&local_30);
  local_30 = 0xca;
  local_28 = 0;
  local_2c = 1;
  local_24 = 0;
  FUN_08004d30(0x50000000,&local_30);
  local_2c = 0x310000;
  local_30 = 4;
  local_28 = 0;
  FUN_08004d30(0x50000000,&local_30);
  local_30 = DAT_08006b7c;
  local_2c = 3;
  local_28 = 0;
  FUN_08004d30(0x50000000,&local_30);
  local_30 = 0xc1;
  local_2c = 3;
  local_28 = 0;
  FUN_08004d30(DAT_08006b70,&local_30);
  local_2c = 0x110000;
  local_30 = 2;
  local_28 = 0;
  FUN_08004d30(DAT_08006b70,&local_30);
  local_28 = 0;
  local_2c = 1;
  local_30 = 4;
  local_24 = 0;
  FUN_08004d30(DAT_08006b70,&local_30);
  local_30 = 0x20;
  local_2c = 0x310000;
  local_28 = 0;
  FUN_08004d30(DAT_08006b70,&local_30);
  case_forward_action(5,3,0);
  case_interrupt_enable(5);
  case_forward_action(6,3,0);
  case_interrupt_enable(6);
  case_forward_action(7,3,0);
  case_interrupt_enable(7);
  return;
}

