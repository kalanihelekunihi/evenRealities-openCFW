
int gx_snpu_exit(void)

{
  int iVar1;
  
  func_0x100254fc(0xc);
  iVar1 = gx8002_snpu_suspend();
  func_0x10025504(0xc);
  if (iVar1 == 0) {
    gx8002_snpu_device_exit();
  }
  return iVar1;
}

