
undefined4 semantic_page_data_unlock(void)

{
  undefined4 unaff_r7;
  
  if (*DAT_0058b344 != 0) {
    osMutexRelease(*DAT_0058b344);
  }
  return unaff_r7;
}

