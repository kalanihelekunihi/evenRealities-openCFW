
void gx8002_clock_lowpower_init_shared(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar4 = 0;
LAB_100259a0:
  do {
    iVar1 = iVar4;
    iVar4 = iVar1 + 1;
    if (iVar1 == 7) {
      iVar2 = gx8002_clock_module_query(7);
      if (iVar2 != 3) goto LAB_100259a0;
      uVar3 = 4;
    }
    else if (iVar1 == 8) {
      iVar2 = gx8002_clock_module_query(8);
      if (iVar2 != 5) goto LAB_100259a0;
      uVar3 = 6;
    }
    else if (iVar1 == 2) {
      iVar1 = gx8002_clock_module_query(2);
      if ((iVar1 == 1) && ((uRam0000008c & 0x40) != 0)) goto LAB_100259a0;
      uVar3 = 0;
      iVar1 = 2;
    }
    else {
      uVar3 = 0;
    }
    gx8002_clock_module_source_fixed(iVar1,uVar3);
    if (iVar4 == 0x1a) {
      return;
    }
  } while( true );
}

