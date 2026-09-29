
void input_msg_send_record(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_005134b4;
  if ((param_1 != 0) && (*(int *)(DAT_005134b4 + 0xc) != 0)) {
    iVar2 = osMessageQueuePut(*(undefined4 *)(DAT_005134b4 + 0xc),param_1,0,0);
    if (iVar2 == 0) {
      osThreadFlagsSet(*(undefined4 *)(iVar1 + 8),0x400000);
    }
    else {
      FUN_004733ee(PTR_s_INP_SendMessage_osMessageQueuePu_0051351c);
    }
  }
  return;
}

