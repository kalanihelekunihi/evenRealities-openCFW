
void gx8002_board_pin_setup(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  iVar1 = gx8002_board_pin_configure(5,0);
  iVar2 = gx8002_board_pin_configure(6,0);
  iVar3 = gx8002_board_pin_configure(0xb,0);
  iVar4 = gx8002_board_pin_configure(0xc,0);
  iVar5 = gx8002_board_pin_configure(7,3);
  iVar6 = gx8002_board_pin_configure(8,3);
  iVar7 = gx8002_board_pin_configure(9,3);
  iVar8 = gx8002_board_pin_configure(10,3);
  if (iVar8 + iVar1 + iVar2 + iVar3 + iVar4 + iVar5 + iVar6 + iVar7 != 0) {
    gx8002_padmux_set(5,0);
    gx8002_padmux_set(6,0);
    gx8002_padmux_set(0xb,0);
    gx8002_padmux_set(0xc,0);
    gx8002_printf(uRam1020689c);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  return;
}

