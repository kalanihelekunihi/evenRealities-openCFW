
undefined4 gx8002_uart_receive_body_done(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = gx8002_channel_lookup(param_1 & 0xff);
  if (iVar1 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    gx8002_uart_body_probe(param_1,iVar1 + 0x1c,0);
    uVar2 = 0;
  }
  return uVar2;
}

