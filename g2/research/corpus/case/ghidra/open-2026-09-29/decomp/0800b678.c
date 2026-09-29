
void case_emit_probe_train(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 in_r3;
  int iVar3;
  byte bVar4;
  
  case_register_write_channel(0x50000000,8,1,in_r3,in_r3);
  osDelay(10);
  iVar1 = DAT_0800b7e4;
  case_register_write_channel(DAT_0800b7e4,0x200);
  osDelay(10);
  case_register_write_channel(iVar1,0x200,0);
  case_busy_delay_alt(0x26c);
  case_register_write_channel(iVar1,0x200,1);
  case_busy_delay_alt(DAT_0800b7e8);
  bVar4 = 0;
  iVar3 = iVar1 >> 0x13;
  do {
    case_register_write_channel(iVar1,0x200,0);
    case_busy_delay_alt(iVar3);
    case_register_write_channel(iVar1,0x200,1);
    case_busy_delay_alt(iVar3);
    bVar4 = bVar4 + 1;
  } while (bVar4 < 5);
  case_register_write_channel(iVar1,0x200,1);
  uVar2 = DAT_0800b7e8;
  case_busy_delay_alt(DAT_0800b7e8);
  case_register_write_channel(iVar1,0x200,0);
  osDelay(0x28);
  case_register_write_channel(iVar1,0x200,1);
  osDelay(1);
  case_register_write_channel(iVar1,0x200,0);
  case_busy_delay_alt(0x26c);
  case_register_write_channel(iVar1,0x200,1);
  case_busy_delay_alt(uVar2);
  bVar4 = 0;
  do {
    case_register_write_channel(iVar1,0x200,0);
    case_busy_delay_alt(iVar3);
    case_register_write_channel(iVar1,0x200,1);
    case_busy_delay_alt(iVar3);
    bVar4 = bVar4 + 1;
  } while (bVar4 < 7);
  case_register_write_channel(iVar1,0x200,1);
  uVar2 = DAT_0800b7e8;
  case_busy_delay_alt(DAT_0800b7e8);
  osDelay(1);
  case_register_write_channel(iVar1,0x200,0);
  case_busy_delay_alt(0x26c);
  case_register_write_channel(iVar1,0x200,1);
  case_busy_delay_alt(uVar2);
  bVar4 = 0;
  do {
    case_register_write_channel(iVar1,0x200,0);
    case_busy_delay_alt(iVar3);
    case_register_write_channel(iVar1,0x200,1);
    case_busy_delay_alt(iVar3);
    bVar4 = bVar4 + 1;
  } while (bVar4 < 7);
  case_register_write_channel(iVar1,0x200,1);
  case_busy_delay_alt(DAT_0800b7e8);
  return;
}

