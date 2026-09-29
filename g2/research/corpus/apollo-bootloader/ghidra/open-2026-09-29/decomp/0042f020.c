
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
register_profile_transfer_42f020(uint *param_1,byte param_2,char param_3,undefined4 param_4)

{
  uint *puVar1;
  uint *puVar2;
  int iVar3;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    iVar3 = 2;
  }
  else {
    if (param_2 == 0) {
      if ((param_3 != '\0') && ((char)param_1[3] == '\0')) {
        iVar3 = 7;
        goto LAB_0042f0e0;
      }
      FUN_0041bf84(0xf);
      if (param_3 != '\0') {
        iVar3 = clock_request(4,0xf);
        if (iVar3 != 0) goto LAB_0042f0e0;
        *_DAT_0042f184 = param_1[5];
        *_DAT_0042f1a8 = param_1[6];
        *_DAT_0042f1ac = param_1[7];
        *_DAT_0042f1b0 = param_1[8];
        *_DAT_0042f1b4 = param_1[9];
        *_DAT_0042f1b8 = param_1[10];
        *_DAT_0042f1bc = param_1[0xb];
        *_DAT_0042f1c0 = param_1[0xc];
        *_DAT_0042f188 = param_1[0xd];
        *_DAT_0042f18c = param_1[0xe];
        *_DAT_0042f190 = param_1[0xf];
        puVar2 = _DAT_0042f1a0;
        *_DAT_0042f1a0 = 0;
        puVar1 = _DAT_0042f180;
        *_DAT_0042f180 = param_1[4] & 0xfffffffe;
        *puVar1 = (byte)param_1[4] & 1 | *puVar1 & 0xfffffffe;
        *puVar2 = param_1[0x10];
        *(undefined1 *)(param_1 + 3) = 0;
      }
    }
    else {
      if ((param_2 != 2) && (1 < param_2)) {
        iVar3 = 6;
        goto LAB_0042f0e0;
      }
      if (param_3 != '\0') {
        param_1[5] = *_DAT_0042f184;
        param_1[6] = *_DAT_0042f1a8;
        param_1[7] = *_DAT_0042f1ac;
        param_1[8] = *_DAT_0042f1b0;
        param_1[9] = *_DAT_0042f1b4;
        param_1[10] = *_DAT_0042f1b8;
        param_1[0xb] = *_DAT_0042f1bc;
        param_1[0xc] = *_DAT_0042f1c0;
        param_1[0xd] = *_DAT_0042f188;
        param_1[0xe] = *_DAT_0042f18c;
        param_1[0xf] = *_DAT_0042f190;
        param_1[0x10] = *_DAT_0042f1a0;
        param_1[4] = *_DAT_0042f180;
        *(undefined1 *)(param_1 + 3) = 1;
      }
      clock_release(4,0xf);
      FUN_0041c17a(0xf);
    }
    iVar3 = 0;
  }
LAB_0042f0e0:
  return CONCAT44(param_4,iVar3);
}

