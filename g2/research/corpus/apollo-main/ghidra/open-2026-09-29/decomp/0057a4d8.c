
undefined8 gx8002_i2s_isr(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int local_10;
  undefined4 uStack_c;
  
  puVar1 = DAT_0057a880;
  local_10 = param_3;
  uStack_c = param_4;
  FUN_00590848(*DAT_0057a880,&local_10,1);
  FUN_00590818(*puVar1,local_10);
  FUN_005908a0(*puVar1,local_10,DAT_0057a884);
  if (local_10 << 0x1b < 0) {
    aud_send_codec_dma_message();
  }
  return CONCAT44(uStack_c,local_10);
}

