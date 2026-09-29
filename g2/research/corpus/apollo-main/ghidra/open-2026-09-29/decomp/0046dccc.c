
void ble_Slave_handler_1(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar2 = productModeGet();
  if (iVar2 == 1) {
    local_14 = 0;
    local_18 = 0;
    local_1c = 0;
    FUN_00475fc0(DAT_0046e03c,DAT_0046e038,&local_14,&local_18,&local_1c);
    iVar2 = DAT_0046e040;
    FUN_004b4728(DAT_0046e040 + 0x13,DAT_0046e044,local_14,local_18,local_1c);
    cVar1 = FUN_0044a43c(iVar2);
    *DAT_0046e00c = cVar1 + '\x01';
  }
  else {
    *(undefined1 *)(DAT_0046e040 + 0x13) = 0;
    *DAT_0046e00c = '\x14';
  }
  iVar2 = DAT_0046e040;
  iVar3 = FUN_0044a43c(DAT_0046e040);
  FUN_00439be4(DAT_0046e048,iVar2,iVar3 + 1);
  return;
}

