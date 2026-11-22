# SPDX-License-Identifier: MIT
"""Fresh compilation and exact-boundary source providers.

Relocation-bearing bodies require an explicit native binding map and isolated
link. Verification stubs and guessed bindings are not production providers.
"""
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def functions(path, include_objects=False):
    data = Path(path).read_bytes()
    if data[:6] != b'\x7fELF\x01\x01':
        raise ValueError('requires little-endian ELF32')
    header = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    machine = header[2]
    if machine not in (40, 195, 252): raise ValueError('requires ARM, ARC, or C-SKY ELF machine')
    sections = [struct.unpack_from('<IIIIIIIIII', data, header[6] + i*header[11]) for i in range(header[12])]
    def content(s): return data[s[4]:s[4]+s[5]]
    def string(table, offset): return table[offset:].split(b'\0', 1)[0].decode()
    names = content(sections[header[13]])
    result = []
    mappings = {}
    for table in sections:
        if table[1] != 2: continue
        strings = content(sections[table[6]])
        for offset in range(table[4], table[4]+table[5], table[9]):
            name,value,size,info,other,index = struct.unpack_from('<IIIBBH',data,offset)
            label=string(strings,name)
            if machine == 40 and label.startswith(('$t','$a','$d')) and index < len(sections):
                mappings.setdefault(index,[]).append(((value & ~1)-sections[index][3], 'data' if label.startswith('$d') else 'code'))
    for table in sections:
        if table[1] != 2: continue
        strings = content(sections[table[6]])
        for offset in range(table[4], table[4]+table[5], table[9]):
            name, value, size, info, other, index = struct.unpack_from('<IIIBBH', data, offset)
            symbol_type=info & 15
            if symbol_type not in ((1,2) if include_objects else (2,)) or index == 0 or index >= len(sections) or not size: continue
            section = sections[index]
            if section[1]==8:continue  # BSS has no stored provider bytes.
            native_value=(value & ~1) if machine == 40 and symbol_type==2 else value
            lo = native_value - section[3]
            relocations = []
            relocation_symbols = []
            relocation_records = []
            for rel in sections:
                if rel[1] in (9, 4) and rel[7] == index:
                    for off in range(rel[4], rel[4]+rel[5], rel[9]):
                        address = struct.unpack_from('<I', data, off)[0]
                        if lo <= address < lo+size:
                            relocations.append(address)
                            rel_info = struct.unpack_from('<I', data, off+4)[0]
                            symbol_table = sections[rel[6]]
                            symbol_offset = symbol_table[4] + (rel_info >> 8)*symbol_table[9]
                            symbol_name, _, _, symbol_info, _, symbol_index = struct.unpack_from(
                                '<IIIBBH', data, symbol_offset)
                            label=string(content(sections[symbol_table[6]]),symbol_name)
                            if not label and symbol_info & 15 == 3 and symbol_index < len(sections):
                                # Local STT_SECTION relocations have no symbol name.
                                # Keep the section identity for an explicit native
                                # scalar binding instead of dropping the relocation.
                                label=string(names, sections[symbol_index][0])
                            relocation_symbols.append(label)
                            relocation_records.append(dict(offset=address-lo,type=rel_info & 255,symbol=label,
                                                           weak_undefined=(symbol_info >> 4 == 2 and symbol_index == 0)))
            markers=sorted(set(mappings.get(index,[])))
            points=sorted({lo,lo+size}|{a for a,k in markers if lo<a<lo+size})
            parts=[]
            for left,right in zip(points,points[1:]):
                kind='data' if symbol_type==1 and not section[2]&4 else next((k for a,k in reversed(markers) if a<=left),'unknown')
                parts.append(dict(start=left-lo,end=right-lo,kind=kind))
            result.append(dict(machine=machine, content_ranges=parts, symbol=string(strings, name), section=string(names, section[0]),
                               symbol_kind='data' if symbol_type==1 else 'function', writable=bool(section[2]&1), address=native_value, size=size, data=content(section)[lo:lo+size], relocations=relocations,
                               relocation_symbols=relocation_symbols, relocation_records=relocation_records,
                               executable=bool(section[2] & 4)))
    return result


def compile_unit(unit, folder):
    folder=folder.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    obj, dep = folder/'unit.o', folder/'unit.d'
    argv = [a.replace('{root}', str(ROOT)) for a in unit['argv']]
    argv += ['-MD', '-MF', str(dep), '-c', str(ROOT/unit['source']), '-o', str(obj)]
    compiler_path=Path(unit['compiler_path'].replace('{root}',str(ROOT))) if unit.get('compiler_path') else None
    if compiler_path and unit.get('compiler_sha256') and sha(compiler_path)!=unit['compiler_sha256']:
        raise ValueError('compiler identity changed')
    before = sha(ROOT/unit['source'])
    dependency_command = [a.replace('{root}', str(ROOT)) for a in unit['argv']]
    preprocessor=subprocess.run([*dependency_command, '-M', '-MF', str(dep), '-MT', 'unit.o',
                    str(ROOT/unit['source'])], cwd=ROOT, capture_output=True, text=True)
    (folder/'preprocess.log').write_text(preprocessor.stdout+preprocessor.stderr)
    if preprocessor.returncode:raise RuntimeError('dependency discovery failed: '+preprocessor.stderr[-1000:])
    deps = shlex.split(dep.read_text().replace('\\\n', ' ').split(':', 1)[1])
    before_inputs = {str(Path(p).resolve()): sha(p) for p in deps}
    process = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    (folder/'compile.log').write_text(process.stdout+process.stderr)
    if process.returncode:
        raise RuntimeError('compile failed: '+process.stderr[-1000:])
    # Dependencies come from the compiler, including headers outside the repo.
    deps = shlex.split(dep.read_text().replace('\\\n', ' ').split(':', 1)[1])
    inputs = {str(Path(p).resolve()): sha(p) for p in deps}
    if before != sha(ROOT/unit['source']) or before_inputs != inputs:
        raise RuntimeError('inputs changed during compile')
    driver = Path(shutil.which(argv[0]) or argv[0]).resolve()
    executable = Path(unit['compiler_path'].replace('{root}', str(ROOT))).resolve() if unit.get('compiler_path') else driver
    receipt = dict(argv=argv, inputs=inputs, compiler=str(executable), compiler_sha256=sha(executable),
                   driver=str(driver), driver_sha256=sha(driver),
                   object_sha256=sha(obj), source=unit['source'])
    return functions(obj), receipt


def build_selected(plan, stage, devices):
    providers, receipts = [], []
    for index, unit in enumerate(plan['units']):
        selected = [r for r in unit['regions'] if r['payload'].split('-')[0] in devices]
        if not selected: continue
        directory = stage/'source-providers'/f'{index:04d}'
        funcs, receipt = compile_unit(unit, directory)
        if any(r.get('symbol_kind')=='data' for r in selected):
            funcs=functions(directory/'unit.o',include_objects=True)
        for item in selected:
            matches = [f for f in funcs if f['symbol'] == item['symbol']]
            if len(matches) != 1: raise ValueError('selected function missing or ambiguous: '+item['symbol'])
            function = matches[0]
            data_provider=item.get('symbol_kind')=='data'
            if data_provider and (function['symbol_kind']!='data' or function['executable'] or function['writable'] or function['relocations']):
                raise ValueError('data provider must be immutable non-executable stored data without relocations')
            if (not data_provider and not function['executable']) or function['size'] != item['end']-item['start']:
                raise ValueError('selected source placement changed: '+item['symbol'])
            data = function['data']
            provider_name=item['symbol']+'-'+format(item['start'],'08x')
            if function['relocations']:
                if not item.get('bindings'):
                    raise ValueError('selected provider has unqualified relocations')
                data, link_command = link_function(directory/'unit.o', function, item['address'],
                                                    item['bindings'], directory/('link-'+provider_name))
                linker = (ROOT/'vendor-cache/g2/csky-abiv2-gcc-6.3/bin/csky-abiv2-elf-ld'
                          if function['machine'] == 252 else
                          ROOT/'vendor-cache/g2/arc-gnu-2026.03/toolchain/arc_gnu_prebuilt_elf32_le_linux_install/arc-multilib-elf32/bin/arc-elf32-ld'
                          if function['machine'] == 195 else Path(shutil.which(link_command[0])))
                receipt.setdefault('links', []).append(dict(argv=link_command,
                    linker=str(linker), linker_sha256=sha(linker),
                    layout_sha256=sha(directory/('link-'+provider_name)/'layout.ld')))
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError('selected source bytes changed: '+item['symbol'])
            path = directory/(provider_name+'.bin')
            path.write_bytes(data)
            providers.append(dict(item, data=path.read_bytes(), file=str(path.relative_to(stage)),
                                  build_receipt=len(receipts), content_ranges=function['content_ranges'],
                                  instruction_origin='assembly' if Path(unit['source']).suffix.lower()=='.s' or item['symbol'] in {'r1_rtt_delay_cycles','ulPortRaiseBASEPRI'} else 'c',
                                  source=unit['source']))
        for path, digest in receipt['inputs'].items():
            if sha(path) != digest: raise ValueError('input changed during build: '+path)
        receipts.append(receipt)
    return providers, receipts


def link_function(obj, function, start_address, bindings, directory):
    """Link one function section using recorded stock symbol bindings only."""
    if function['machine'] == 252:
        return link_csky_function(obj, function, start_address, bindings, directory)
    if function['machine'] == 195:
        return link_arc_function(obj, function, start_address, bindings, directory)
    if function['machine'] != 40:
        raise ValueError('unsupported isolated relocation architecture')
    # A function sharing .text with other bodies cannot be isolated by this path.
    if not function['section'].startswith('.text.'):
        raise ValueError('function has no isolated text section')
    directory.mkdir(parents=True, exist_ok=True)
    script = directory/'layout.ld'
    # A relocation can target a local function or STT_SECTION symbol defined
    # in this same object. --defsym cannot replace either when its owning
    # section is discarded. Retain just those sections at independently
    # recovered stock addresses; all other sections remain discarded.
    # Legacy plans intentionally bind callable symbols with --defsym. Section
    # symbols mark a recipe that also needs same-object local placement.
    retain_locals = any(name.startswith('.') for name in bindings)
    local_functions = {f['symbol']: f['section'] for f in functions(obj)} if retain_locals else {}
    bound_sections = {}
    defsyms = {}
    for name, address in bindings.items():
        if address is None:
            continue
        section = name if retain_locals and name.startswith('.') else local_functions.get(name)
        if section and section != function['section']:
            placement = address & ~1 if section.startswith('.text.') else address
            if section in bound_sections and bound_sections[section] != placement:
                raise ValueError('conflicting local section bindings')
            bound_sections[section] = placement
        else:
            defsyms[name] = address
    lines = [f"SECTIONS {{ .provider 0x{start_address:x} : {{ *({function['section']}) }}"]
    lines += [f".bound{i} 0x{address:x} : {{ *({section}) }}"
              for i, (section, address) in enumerate(sorted(bound_sections.items()))]
    lines += ['/DISCARD/ : { *(*) } }']
    script.write_text('\n'.join(lines) + '\n')
    elf = directory/'provider.elf'
    command = ['arm-none-eabi-ld','-T',str(script),'-o',str(elf),str(obj)]
    # A None binding deliberately leaves a weak undefined symbol unresolved.
    # GNU ld then performs its native weak-call relaxation, which differs from
    # forcing the symbol to the absolute value zero with --defsym.
    command += [f'--defsym={name}=0x{address:x}' for name,address in sorted(defsyms.items())]
    process = subprocess.run(command, capture_output=True, text=True)
    (directory/'link.log').write_text(process.stdout+process.stderr)
    if process.returncode: raise ValueError('production bindings do not close isolated function link')
    result = next((f for f in functions(elf) if f['symbol']==function['symbol']), None)
    if result is None or result['relocations'] or result['size'] != function['size'] or result['address'] != start_address:
        raise ValueError('linked function shape changed')
    return result['data'], command


def link_csky_function(obj, function, start_address, bindings, directory):
    """Resolve only isolated C-SKY call relocations to proven stock callees."""
    if function['machine'] != 252 or not function['section'].startswith('.text.'):
        raise ValueError('C-SKY function lacks an isolated text section')
    if any(record['type'] != 19 or record['symbol'] not in bindings
           for record in function['relocation_records']):
        raise ValueError('C-SKY provider has an unsupported or unbound relocation')
    if any(not isinstance(address, int) or address < 0x10000000 or address >= 0x10010000
           for address in bindings.values()):
        raise ValueError('C-SKY callee binding is outside the UART virtual image')
    sharing = [candidate for candidate in functions(obj)
               if candidate['section'] == function['section']]
    if len(sharing) != 1 or sharing[0]['symbol'] != function['symbol']:
        raise ValueError('C-SKY function section is not isolated')
    directory.mkdir(parents=True, exist_ok=True)
    script = directory/'layout.ld'
    script.write_text(f'SECTIONS {{ .provider 0x{start_address:x} : '
                      f'{{ *({function["section"]}) }} /DISCARD/ : {{ *(*) }} }}\n')
    tool = (ROOT/'vendor-cache/g2/csky-abiv2-gcc-6.3').resolve()
    linker = tool/'bin/csky-abiv2-elf-ld'
    if not linker.is_file():
        raise ValueError('C-SKY linker is unavailable')
    elf = directory/'provider.elf'
    command = ['docker', 'run', '--rm', '--network=none', '--platform', 'linux/amd64',
               '--mount', f'type=bind,src={tool},dst=/tool,readonly',
               '--mount', f'type=bind,src={Path(obj).parent.resolve()},dst=/input,readonly',
               '--mount', f'type=bind,src={directory.resolve()},dst=/output',
               '--entrypoint', '/tool/bin/csky-abiv2-elf-ld', 'ubuntu:24.04',
               '-T', '/output/layout.ld', '-o', '/output/provider.elf',
               f'/input/{Path(obj).name}',
               *[f'--defsym={name}=0x{address:x}' for name,address in sorted(bindings.items())]]
    process = subprocess.run(command, capture_output=True, text=True)
    (directory/'link.log').write_text(process.stdout+process.stderr)
    if process.returncode:
        raise ValueError('C-SKY stock bindings do not close isolated function link')
    result = [f for f in functions(elf) if f['symbol'] == function['symbol']]
    if (len(result) != 1 or result[0]['relocations'] or result[0]['size'] != function['size']
            or result[0]['address'] != start_address):
        raise ValueError('C-SKY linked function shape changed')
    return result[0]['data'], command


def link_arc_function(obj, function, start_address, bindings, directory):
    """Resolve isolated ARC calls and code pointers against inventoried entries."""
    if function['machine'] != 195 or not function['section'].startswith('.text.'):
        raise ValueError('ARC function lacks an isolated text section')
    if any(record['type'] not in (16, 17, 27) or record['weak_undefined'] or
           record['symbol'] not in bindings for record in function['relocation_records']):
        raise ValueError('ARC provider has an unsupported or unbound relocation')
    if any(not isinstance(address, int) or address < 0x302400 or address >= 0x335bc8
           for address in bindings.values()):
        raise ValueError('ARC binding is outside the inventoried record-3 image')
    sharing = [candidate for candidate in functions(obj)
               if candidate['section'] == function['section']]
    if len(sharing) != 1 or sharing[0]['symbol'] != function['symbol']:
        raise ValueError('ARC function section is not isolated')
    directory.mkdir(parents=True, exist_ok=True)
    script = directory/'layout.ld'
    script.write_text(f'SECTIONS {{ .provider 0x{start_address:x} : '
                      f'{{ *({function["section"]}) }} /DISCARD/ : {{ *(*) }} }}\n')
    tool = (ROOT/'vendor-cache/g2/arc-gnu-2026.03/toolchain/'
            'arc_gnu_prebuilt_elf32_le_linux_install/arc-multilib-elf32').resolve()
    linker = tool/'bin/arc-elf32-ld'
    if not linker.is_file():
        raise ValueError('ARC linker is unavailable')
    elf = directory/'provider.elf'
    command = ['docker', 'run', '--rm', '--network=none', '--platform', 'linux/amd64',
               '--mount', f'type=bind,src={tool},dst=/tool,readonly',
               '--mount', f'type=bind,src={Path(obj).parent.resolve()},dst=/input,readonly',
               '--mount', f'type=bind,src={directory.resolve()},dst=/output',
               '--entrypoint', '/tool/bin/arc-elf32-ld',
               'opencfw/iar-base:10.10.2-local',
               '-T', '/output/layout.ld', '-o', '/output/provider.elf',
               f'/input/{Path(obj).name}',
               *[f'--defsym={name}=0x{address:x}' for name,address in sorted(bindings.items())]]
    process = subprocess.run(command, capture_output=True, text=True)
    (directory/'link.log').write_text(process.stdout+process.stderr)
    if process.returncode:
        raise ValueError('ARC stock bindings do not close isolated function link')
    result = [f for f in functions(elf) if f['symbol'] == function['symbol']]
    if (len(result) != 1 or result[0]['relocations'] or result[0]['size'] != function['size']
            or result[0]['address'] != start_address):
        raise ValueError('ARC linked function shape changed')
    return result[0]['data'], command
