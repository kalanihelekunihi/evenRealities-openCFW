
undefined4 atImuRawDataHandler(void)

{
  int iVar1;
  
  iVar1 = thunk_FUN_0048d86c();
  if (iVar1 == 1) {
    hub_msg_send_id4(1);
  }
  else {
    if (iVar1 != 0) {
      at_core_output(PTR_s_AT_IMU_RAWDATA_ERROR__invalid_pa_005a58a0);
      return 0;
    }
    hub_msg_send_id4(0);
  }
  at_core_output(PTR_s_AT_IMU_RAWDATA_OK_type__d_005a589c,iVar1);
  return 1;
}

