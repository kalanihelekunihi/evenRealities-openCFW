
undefined8
aud_send_message_type1(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_18;
  undefined4 local_14;
  uint local_10;
  undefined4 uStack_c;
  
  local_18 = 1;
  local_14 = 1;
  local_10 = param_1 & 0xff;
  uStack_c = param_4;
  AUD_SendMessage(&local_18);
  return CONCAT44(local_14,local_18);
}

