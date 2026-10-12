set pagination off
target remote host.docker.internal:12349
break *0x1000d46c
commands
  silent
  printf "entry r0=%x r1=%x r3=%x\n", $r0, $r1, $r3
  continue
end
break *0x1000d6c4
commands
  silent
  printf "frame-test r2=%x\n", $r2
  continue
end
break *0x1000db5c
commands
  silent
  printf "output-prep sp=%x\n", $sp
  continue
end
break *0x1000dba2
commands
  silent
  printf "channel-test r9=%x\n", $r9
  continue
end
break *0x1000dcd4
commands
  silent
  printf "finish sp=%x\n", $sp
  continue
end
break *0x1000dd38
commands
  silent
  printf "return sp=%x\n", $sp
  continue
end
continue
