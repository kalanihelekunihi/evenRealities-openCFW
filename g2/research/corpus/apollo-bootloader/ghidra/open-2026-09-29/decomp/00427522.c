
undefined8 syspll_lock_wait_427522(uint *param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004275ac)) {
    uVar1 = 2;
  }
  else if ((int)(*DAT_004275b4 << 2) < 0) {
    if ((*DAT_004275b4 >> 9 & 1) == 1) {
      iVar2 = 0x753;
    }
    else {
      iVar2 = 1000;
    }
    unaff_r7 = 1;
    uVar1 = delay_us_status_check(((*DAT_004275bc & 0x3f) * iVar2 + 0xb) / 0xc,DAT_004275c0,1,1);
  }
  else {
    uVar1 = 7;
  }
  return CONCAT44(unaff_r7,uVar1);
}

