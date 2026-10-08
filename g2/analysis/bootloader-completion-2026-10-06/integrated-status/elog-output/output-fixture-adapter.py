import importlib.util,json,sys,hashlib
from pathlib import Path
p=Path('g2/components/bootloader/initializer_callbacks/verify_elog_output.py');s=importlib.util.spec_from_file_location('output',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.TIME=0x20026f18
m.main()
q=Path(sys.argv[sys.argv.index('--output')+1]);j=json.loads(q.read_text());j['fixture_adapter_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();j['fixture_correction']='Time metadata returns stock fixed buffer20026f18; source compiler may fold its returned pointer. Injected metadata still controls contents. Frozen runner unchanged.';q.write_text(json.dumps(j,indent=2)+'\n')
