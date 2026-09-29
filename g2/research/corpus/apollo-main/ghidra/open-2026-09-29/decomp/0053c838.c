
undefined4 aud_codec_route_control(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == '\0') {
    SVC_CodecDMICClose();
    SVC_I2SOutputCtrl(0);
    DRV_Gx8002_I2SDeinit();
  }
  else {
    SVC_CodecDMICOpen();
    SVC_I2SOutputCtrl(1);
    DRV_Gx8002_I2SInit();
  }
  return unaff_r7;
}

