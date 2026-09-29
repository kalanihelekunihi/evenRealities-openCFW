
undefined4 quicklist_unlock_storage(void)

{
  undefined4 unaff_r7;
  
  if (*DAT_004ffba8 != 0) {
    osMutexRelease(*DAT_004ffba8);
  }
  return unaff_r7;
}

