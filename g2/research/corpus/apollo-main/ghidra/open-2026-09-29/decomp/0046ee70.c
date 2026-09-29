
undefined8 APP_BleSlaveAdvStartEvent(void)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  puVar2 = (undefined2 *)WsfMsgAlloc(0xc);
  if (puVar2 != (undefined2 *)0x0) {
    *(undefined1 *)(puVar2 + 1) = 0xb6;
    *puVar2 = 0xff;
    WsfMsgSend(*(undefined1 *)(*DAT_0046f3c4 + 0x56),puVar2);
    iVar3 = FUN_0043d0ce();
    uVar1 = DAT_0046f424;
    if (iVar3 << 0x1e < 0) {
      unaff_r5 = 0x28c;
      FUN_0043d574(3,DAT_0046f404,DAT_0046f400,DAT_0046f428);
      unaff_r6 = uVar1;
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__ble_Slave_EVEN_SLAVE_ADV_AGAIN__0046f42c,
                          PTR_s__ble_Slave_EVEN_SLAVE_ADV_AGAIN__0046f42c);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

