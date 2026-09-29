
undefined4 gx8002_board_pin_configure(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((*piRam10206814 == 0) && (iVar1 = gx8002_padmux_check(param_1,param_1 != 2), iVar1 != 0)) {
    gx8002_printf(uRam10206818,param_1);
    uVar2 = 0xffffffff;
  }
  else {
    gx8002_padmux_set(param_1,param_2);
    uVar2 = 0;
  }
  return uVar2;
}

