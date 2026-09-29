
undefined4 health_unlock_storage(void)

{
  undefined4 unaff_r7;
  
  if (*DAT_004ffdd0 != 0) {
    osMutexRelease(*DAT_004ffdd0);
  }
  return unaff_r7;
}

