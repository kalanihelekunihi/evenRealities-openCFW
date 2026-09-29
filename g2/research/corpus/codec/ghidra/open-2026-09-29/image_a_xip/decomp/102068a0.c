
void gx8002_board_pin_initialize(void)

{
  char cVar1;
  char cVar2;
  undefined *puVar3;
  undefined *puVar4;
  int iVar5;
  int iVar6;
  
  gx8002_padmux_init(PTR_gx8002_board_pin_defaults_102068fc,0xd);
  puVar4 = PTR_s_pin__d_set_error__10206900;
  puVar3 = PTR_gx8002_board_pin_defaults_102068fc;
  iVar6 = 1;
  do {
    cVar1 = puVar3[iVar6 * 2 + -2];
    cVar2 = puVar3[iVar6 * 2 + -1];
    iVar5 = gx8002_padmux_check(cVar1,cVar2);
    if (iVar5 != 0) {
      gx8002_printf(puVar4,cVar1);
    }
    if (cVar1 == '\x02') {
      if (cVar2 == '\0') {
LAB_102068f0:
        gx_gpio_set_direction(cVar1,0);
      }
    }
    else if (cVar2 == '\x01') goto LAB_102068f0;
    iVar6 = iVar6 + 1;
    if (iVar6 == 0xe) {
      gx8002_board_pin_setup();
      *puRam10206904 = 1;
      return;
    }
  } while( true );
}

