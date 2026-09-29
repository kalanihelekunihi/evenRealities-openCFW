
undefined4 FUN_10005a5c(int param_1,uint param_2,uint param_3,uint param_4)

{
  uint *puVar1;
  uint *puVar2;
  
  puVar2 = DAT_10005ab0;
  puVar1 = DAT_10005aac;
  if (param_1 == 1) {
    puVar2 = (uint *)&DAT_a0a00010;
  }
  else if (param_1 == 2) {
    *DAT_10005ab0 = *DAT_10005ab0 & 0xefffffff;
  }
  else if (param_1 == 4) {
    *DAT_10005aac = *DAT_10005aac & 0xefffffff;
    puVar2 = puVar1;
  }
  else {
    puVar2 = (uint *)0x0;
  }
  puVar2[2] = param_2;
  puVar2[3] = param_3;
  puVar2[4] = param_4;
  return 0;
}

