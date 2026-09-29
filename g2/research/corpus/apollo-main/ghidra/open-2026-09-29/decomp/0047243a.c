
int FUN_0047243a(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  undefined4 in_r3;
  undefined1 local_20;
  bool local_1f;
  undefined4 uStack_1c;
  
  uStack_1c = in_r3;
  cVar1 = FUN_004acad0();
  cVar2 = FUN_00443484();
  cVar3 = semantic_get_aid_enabled();
  cVar4 = FUN_0049eb8e();
  FUN_0043c0e4(&local_20,2,0);
  if ((cVar3 == '\0') || (cVar4 == '\x02')) {
    local_20 = 1;
  }
  else {
    local_20 = 0;
  }
  if (cVar1 == '\x01') {
    local_20 = 0;
  }
  local_1f = cVar1 != '\x01' && cVar2 == '\x01';
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00472bbc,DAT_00472bb8,DAT_00472bd8,0x187,DAT_00472bd4,cVar1,cVar4,cVar3,cVar2
                 ,local_20,local_1f);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0xd800000,DAT_00472bdc,DAT_00472bdc,cVar1,cVar4,cVar3,cVar2,local_20,
                        local_1f);
  }
  cVar1 = ring_task_msg_send(0x400,&local_20,2);
  return (int)cVar1;
}

