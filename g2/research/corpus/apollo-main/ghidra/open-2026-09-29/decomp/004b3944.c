
undefined8 FUN_004b3944(undefined2 *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int *local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  *(undefined1 *)((int)param_2 + 6) = 0;
  *(undefined1 *)((int)param_2 + 7) = 0;
  local_18 = param_2;
  local_14 = param_3;
  uStack_10 = param_4;
  iVar2 = FUN_0047ad74(*(undefined1 *)((int)param_1 + 9),param_1 + 5);
  *param_2 = iVar2;
  if (((*param_2 == 0) && (*(char *)((int)param_1 + 9) == '\x01')) &&
     ((*(byte *)((int)param_1 + 0xf) & 0xc0) == 0x40)) {
    FUN_00479418();
    FUN_004b3606(param_1);
  }
  else if (*param_2 != 0) {
    *DAT_004b43f8 = 1;
    if (*param_2 != 0) {
      if (*param_2 + 0x6c != 0) {
        AttsCccInitTable((char)param_2[1],*param_2 + 0x6c);
      }
      FUN_0047b40c(*param_2,&local_18,&local_14);
      AttsCsfConnOpen((char)param_2[1],(uint)local_18 & 0xff,local_14);
    }
  }
  piVar1 = DAT_004b4508;
  if ((*(char *)(*DAT_004b4508 + 4) != '\0') && (iVar2 = FUN_0047a600(), iVar2 != 0)) {
    DmSecSlaveReq((char)*param_1,*(undefined1 *)*piVar1);
  }
  return CONCAT44(local_14,local_18);
}

