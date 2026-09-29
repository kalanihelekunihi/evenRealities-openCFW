
undefined8 FUN_0055e09c(uint *param_1,byte param_2,char param_3,undefined4 param_4)

{
  uint *puVar1;
  uint *puVar2;
  int iVar3;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    iVar3 = 2;
  }
  else {
    if (param_2 == 0) {
      if ((param_3 != '\0') && ((char)param_1[3] == '\0')) {
        iVar3 = 7;
        goto LAB_0055e15c;
      }
      FUN_0047f5b8(0xf);
      if (param_3 != '\0') {
        iVar3 = FUN_004c44bc(4,0xf);
        if (iVar3 != 0) goto LAB_0055e15c;
        *DAT_0055e200 = param_1[5];
        *DAT_0055e224 = param_1[6];
        *DAT_0055e228 = param_1[7];
        *DAT_0055e22c = param_1[8];
        *DAT_0055e230 = param_1[9];
        *DAT_0055e234 = param_1[10];
        *DAT_0055e238 = param_1[0xb];
        *DAT_0055e23c = param_1[0xc];
        *DAT_0055e204 = param_1[0xd];
        *DAT_0055e208 = param_1[0xe];
        *DAT_0055e20c = param_1[0xf];
        puVar2 = DAT_0055e21c;
        *DAT_0055e21c = 0;
        puVar1 = DAT_0055e1fc;
        *DAT_0055e1fc = param_1[4] & 0xfffffffe;
        *puVar1 = (byte)param_1[4] & 1 | *puVar1 & 0xfffffffe;
        *puVar2 = param_1[0x10];
        *(undefined1 *)(param_1 + 3) = 0;
      }
    }
    else {
      if ((param_2 != 2) && (1 < param_2)) {
        iVar3 = 6;
        goto LAB_0055e15c;
      }
      if (param_3 != '\0') {
        param_1[5] = *DAT_0055e200;
        param_1[6] = *DAT_0055e224;
        param_1[7] = *DAT_0055e228;
        param_1[8] = *DAT_0055e22c;
        param_1[9] = *DAT_0055e230;
        param_1[10] = *DAT_0055e234;
        param_1[0xb] = *DAT_0055e238;
        param_1[0xc] = *DAT_0055e23c;
        param_1[0xd] = *DAT_0055e204;
        param_1[0xe] = *DAT_0055e208;
        param_1[0xf] = *DAT_0055e20c;
        param_1[0x10] = *DAT_0055e21c;
        param_1[4] = *DAT_0055e1fc;
        *(undefined1 *)(param_1 + 3) = 1;
      }
      FUN_004c4530(4,0xf);
      FUN_0047f7ae(0xf);
    }
    iVar3 = 0;
  }
LAB_0055e15c:
  return CONCAT44(param_4,iVar3);
}

