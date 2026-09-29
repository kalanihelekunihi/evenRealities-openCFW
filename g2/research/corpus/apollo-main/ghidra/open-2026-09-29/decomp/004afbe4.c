
undefined * nvdbSysDtMonth(byte param_1)

{
  undefined *puVar1;
  undefined *puVar2;
  
  puVar1 = DAT_004b0368;
  puVar2 = PTR_s_unknow_004b0364;
  if (param_1 - 0x41 < 0x1a) {
    FUN_004b4728(DAT_004b0368,&DAT_004afcb4,param_1 - 0x40);
    puVar2 = puVar1;
  }
  return puVar2;
}

