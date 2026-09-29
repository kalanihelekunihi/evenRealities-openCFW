
void gx8002_snpu_dump_words(undefined4 *param_1)

{
  undefined *puVar1;
  undefined *puVar2;
  int iVar3;
  
  puVar2 = PTR_DAT_10205b18;
  puVar1 = PTR_s_0x_08x_10205b14;
  iVar3 = 0;
  do {
    iVar3 = iVar3 + 1;
    gx8002_printf(puVar1,*param_1);
    if (iVar3 % 10 == 0) {
      gx8002_printf(puVar2);
    }
    param_1 = param_1 + 1;
  } while (iVar3 != 0x20);
  gx8002_printf(PTR_DAT_10205b18);
  return;
}

