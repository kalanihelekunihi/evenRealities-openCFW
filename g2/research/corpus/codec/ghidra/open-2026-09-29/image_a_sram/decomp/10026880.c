
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx_clock_dto_table(void)

{
  undefined1 uVar1;
  byte in_psr;
  
  uVar1 = (undefined1)uRam10026c5c;
  if ((bool)(in_psr & 1)) {
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
    stub();
  }
  else {
    uVar1 = (undefined1)uRam10026c1c;
    if ((bool)(in_psr & 1)) {
      stub();
      stub();
LAB_100269b0:
      stub();
      stub();
      stub();
LAB_100269b8:
      stub();
      stub();
    }
    else {
      uVar1 = (undefined1)uRam10026c24;
      if (!(bool)(in_psr & 1)) goto LAB_100269b8;
      uVar1 = (undefined1)uRam10026c2c;
      if ((bool)(in_psr & 1)) goto LAB_100269b0;
      uVar1 = (undefined1)uRam10026c30;
      if (!(bool)(in_psr & 1)) {
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
        stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
        halt_baddata();
      }
    }
    stub();
    stub();
    stub();
    stub();
    if ((bool)(in_psr & 1)) {
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      goto LAB_10026b10;
    }
  }
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
LAB_10026b10:
  stub();
  stub();
  stub();
  stub();
  *puRam10026f0c = uVar1;
  stub();
  stub();
  stub();
  stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

