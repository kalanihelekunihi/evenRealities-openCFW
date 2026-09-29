
void smpScActJwncDisplay(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  ushort local_28;
  undefined1 local_26;
  undefined1 local_25;
  ushort local_24;
  undefined1 local_22;
  undefined1 local_21;
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if (*(char *)(*(int *)(param_1 + 0x48) + 1) == '\x04') {
    smpLogByteArray(PTR_s_JWNC_Display_Cnf_005e3104,*(undefined4 *)(param_2 + 4),0x10);
    FUN_00542a44(auStack_20,*(undefined4 *)(param_2 + 4));
    local_24 = (ushort)*(byte *)(param_1 + 0x3d);
    local_22 = 0x35;
    local_21 = 0;
    DmSmpCbackExec(&local_24);
  }
  else {
    local_28 = (ushort)*(byte *)(param_1 + 0x3d);
    local_26 = 0x16;
    local_25 = 0;
    smpSmExecute(param_1,&local_28);
  }
  return;
}

