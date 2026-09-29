
undefined8 FUN_0055e070(uint *param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  puVar3 = DAT_0055e240;
  puVar1 = (undefined4 *)param_1[1];
  if ((param_1 == (uint *)0x0) ||
     (puVar1 = DAT_0055e1f8, (undefined4 *)(*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    puVar3 = puVar1;
    uVar2 = 2;
  }
  else {
    *DAT_0055e240 = 0x37;
    uVar2 = 0;
  }
  return CONCAT44(puVar3,uVar2);
}

