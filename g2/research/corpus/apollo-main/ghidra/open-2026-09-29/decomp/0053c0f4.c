
longlong bq27427_init_wrapper(void)

{
  uint unaff_r7;
  
  bq27427_status_update();
  return (ulonglong)unaff_r7 << 0x20;
}

