
void gx8002_watchdog_initialize
               (undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 < 1000) {
    gx8002_printf(uRam10206794);
  }
  else {
    func_0x10025080(0x18,1);
    uVar1 = uRam1020679c;
    uRam00000004 = 0;
    iVar2 = 0x10;
    do {
      if (param_2 / 1000 <= (uint)((1 << (uRam00000004 + 0x10 & 0x3f)) / 1000000))
      goto LAB_1020676c;
      uRam00000004 = uRam00000004 + 1;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
    uRam00000004 = 0xf;
LAB_1020676c:
    uRam00000004 = uRam00000004 | uRam00000004 << 4;
    uRam0000000c = 0x76;
    *puRam10206798 = param_3;
    func_0x1002553c(0xb,uVar1,param_4);
    uRam00000000 = uRam00000000 | 1;
  }
  return;
}

