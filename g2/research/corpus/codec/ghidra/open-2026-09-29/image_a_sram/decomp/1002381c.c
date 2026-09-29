
undefined4 gx8002_flash_read(int param_1,int param_2,int param_3)

{
  int iVar1;
  int unaff_r5;
  
  gx8002_flash_wait_ready();
  iVar1 = DAT_10023854;
  for (; param_3 != 0; param_3 = param_3 - unaff_r5) {
    unaff_r5 = (uint)(param_3 < 0x10000) * unaff_r5 + (uint)(param_3 >= 0x10000) * 0x10000;
    (*(code *)(*(uint *)(iVar1 + 0x1c) & 0xfffffffe))(param_1,param_2,unaff_r5);
    param_1 = param_1 + unaff_r5;
    param_2 = param_2 + unaff_r5;
  }
  return 0;
}

