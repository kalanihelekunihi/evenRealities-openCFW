
undefined8 FUN_004e1406(int param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == 1) {
    if (*DAT_004e19bc == 0) {
      *DAT_004e19bc = 1;
      AUDM_appAcquire(5);
      goto LAB_004e143a;
    }
  }
  if ((param_1 == 0) && (*DAT_004e19bc == 1)) {
    *DAT_004e19bc = 0;
    AUDM_appRelease(5);
  }
LAB_004e143a:
  return CONCAT44(unaff_r7,*DAT_004e19bc);
}

