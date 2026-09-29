
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 hub_imu_register_write(void)

{
  undefined4 unaff_r7;
  
  DRV_IMUReadData(*_DAT_004a7360);
  return unaff_r7;
}

