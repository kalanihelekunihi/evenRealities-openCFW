
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx_clock_div_table(undefined4 param_1,undefined1 param_2)

{
  byte in_psr;
  
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
    param_2 = (undefined1)_gx8002_aout_hw_settings;
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
      param_2 = (undefined1)uRam10026c24;
      if (!(bool)(in_psr & 1)) goto LAB_100269b8;
      param_2 = (undefined1)uRam10026c2c;
      if ((bool)(in_psr & 1)) goto LAB_100269b0;
      param_2 = (undefined1)uRam10026c30;
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
  *puRam10026f0c = param_2;
  stub();
  stub();
  stub();
  stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

