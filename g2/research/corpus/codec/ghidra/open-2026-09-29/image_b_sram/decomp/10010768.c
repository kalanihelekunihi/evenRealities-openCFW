
/* WARNING: Control flow encountered bad instruction data */

uint FUN_10010768(uint param_1)

{
  uint uVar1;
  int iVar2;
  float in_vr0;
  
  if (((uint)in_vr0 & 0x3fffffff) != 0) {
    if ((int)in_vr0 < 0) {
      return param_1;
    }
    if (-1 < (int)in_vr0) {
      return 0xffffffff;
    }
    if ((int)in_vr0 < 0x800000) {
      in_vr0 = in_vr0 * 0.0;
      iVar2 = -0x19;
    }
    else {
      iVar2 = 0;
    }
    uVar1 = (uint)in_vr0 & 0x3fffff;
    iVar2 = ((int)in_vr0 >> 0x17) + -0x7f + iVar2;
    if ((uVar1 + 0xf & 0x3fffff) < 0x10) {
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
    param_1 = uVar1 + DAT_10010990;
    if ((int)(DAT_100109b0 - uVar1 | param_1) < 1) {
      param_1 = DAT_100109bc;
      if (iVar2 == 0) {
                    /* WARNING: Bad instruction - Truncating control flow here */
        halt_baddata();
      }
    }
    else if (iVar2 == 0) {
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
  }
  return param_1;
}

