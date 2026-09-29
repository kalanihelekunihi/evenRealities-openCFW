
void peripheral_mode_write_retry
               (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  char local_10;
  undefined3 uStack_f;
  
  uStack_f = (undefined3)((uint)param_4 >> 8);
  if (param_1 == 0) {
    _local_10 = CONCAT31(uStack_f,9);
    bVar1 = 0;
    while( true ) {
      right_channel_transaction_guard(0x15,8);
      peripheral_transaction_guard(0x15,&local_10,1);
      bVar1 = bVar1 + 1;
      if (local_10 == '\b') break;
      if (2 < bVar1) {
        return;
      }
    }
  }
  else {
    _local_10 = CONCAT31(uStack_f,8);
    bVar1 = 0;
    do {
      right_channel_transaction_guard(0x15,9);
      peripheral_transaction_guard(0x15,&local_10,1);
      bVar1 = bVar1 + 1;
      if (local_10 == '\t') {
        return;
      }
    } while (bVar1 < 3);
  }
  return;
}

