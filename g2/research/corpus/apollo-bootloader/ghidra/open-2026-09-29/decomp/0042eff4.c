
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 hw_handle_command_42eff4(uint *param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  puVar3 = _DAT_0042f1c4;
  puVar1 = (undefined4 *)param_1[1];
  if ((param_1 == (uint *)0x0) ||
     (puVar1 = _DAT_0042f17c, (undefined4 *)(*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    puVar3 = puVar1;
    uVar2 = 2;
  }
  else {
    *_DAT_0042f1c4 = 0x37;
    uVar2 = 0;
  }
  return CONCAT44(puVar3,uVar2);
}

