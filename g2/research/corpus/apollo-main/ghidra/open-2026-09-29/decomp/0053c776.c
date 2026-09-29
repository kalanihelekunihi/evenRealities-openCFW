
undefined8 aud_pdm_counter_sample(void)

{
  int iVar1;
  
  iVar1 = productModeGet();
  if ((iVar1 == 1) && (*DAT_0053cee0 == '\0')) {
    drv_pdm_production_buffer_get(&stack0xfffffff4,&stack0xfffffff0);
  }
  else {
    drv_pdm_buffer_get(&stack0xfffffff4,&stack0xfffffff0);
  }
  SVC_PcmAppProcessData(1,0,0);
  return 0;
}

