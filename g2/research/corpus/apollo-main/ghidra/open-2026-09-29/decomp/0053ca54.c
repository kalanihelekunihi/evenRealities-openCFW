
undefined8
aud_send_message_type4(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uStack_18;
  undefined4 uStack_14;
  uint uStack_10;
  undefined4 uStack_c;
  
  uStack_14 = 0;
  uStack_18 = 4;
  uStack_10 = param_1 & 0xff;
  uStack_c = param_4;
  AUD_SendMessage(&uStack_18);
  return CONCAT44(uStack_14,uStack_18);
}

