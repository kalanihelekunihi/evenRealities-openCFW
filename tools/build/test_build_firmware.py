# SPDX-License-Identifier: MIT
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('hybrid', Path(__file__).with_name('build_firmware.py'))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class HybridTest(unittest.TestCase):
    def test_resource_accounting_and_reuse(self):
        stock = b'abcdefgh'
        m = {'payload': 'test', 'sha256': b.cut.sha256(stock), 'regions': [
            {'label': 'mixed', 'start': '0x0', 'end': '0x8', 'state': 'retained'}]}
        asset = {'kind': 'font', 'start': 2, 'end': 5, 'payload_sha256': m['sha256'], 'sha256': b.cut.sha256(stock[2:5])}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image, report = b.compose(m, stock, root/'compiled', {}, [asset], root)
            self.assertEqual(image, stock)
            self.assertEqual(report['totals'], {'binary-pull-through': 5, 'resource-file': 3})
            self.assertEqual((root/asset['file']).read_bytes(), b'cde')
            with self.assertRaises(b.cut.CutError):
                b.compose(m, stock, root, {}, [asset, asset], root)
            asset['sha256'] = 'bad'
            with self.assertRaises(b.cut.CutError):
                b.compose(m, stock, root, {}, [asset], root)

    def test_source_build_and_no_silent_fallback(self):
        stock = b'abcd'
        m = {'payload': 'test', 'sha256': b.cut.sha256(stock), 'regions': [
            {'label': 'code', 'start': '0x0', 'end': '0x4', 'state': 'source'}]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(b.cut.CutError):
                b.compose(m, stock, root, {}, [], root)
            # Fixture command stands in for a compiler; provenance binds inputs and invocation.
            recipe = {'test/code': {'inputs': ['tools/build/test_build_firmware.py'],
                'argv': [b.sys.executable, '-c', 'import pathlib,sys;pathlib.Path(sys.argv[1]).write_bytes(b"abcd")', '{output}']}}
            image, report = b.compose(m, stock, root/'compiled', recipe, [], root)
            self.assertEqual(image, stock)
            self.assertEqual(report['totals'], {'source-built': 4})
            with self.assertRaises(b.cut.CutError):
                b.compose(m, stock, root/'compiled', recipe, [], root)

class CompiledProviderTest(unittest.TestCase):
    def test_compiled_provider_is_consumed_and_resource_overlap_rejected(self):
        stock = b'abcdefgh'
        m = {'payload': 'test', 'sha256': b.cut.sha256(stock), 'regions': [
            {'label': 'mixed', 'start': '0x0', 'end': '0x8', 'state': 'retained'}]}
        provider = dict(start=2, end=5, data=b'cde', sha256=b.cut.sha256(b'cde'), symbol='fn', build_receipt=0)
        asset = dict(start=3,end=6,sha256=b.cut.sha256(b'def'),payload_sha256=m['sha256'],kind='font')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image, report = b.compose(m,stock,root,{},[],root,[provider])
            self.assertEqual(image,stock)
            self.assertEqual(report['totals'],{'binary-pull-through':5,'source-built':3})
            with self.assertRaises(b.cut.CutError):
                b.compose(m,stock,root,{},[asset],root,[provider])
            provider['data']=b'bad'
            with self.assertRaises(b.cut.CutError):
                b.compose(m,stock,root,{},[],root,[provider])


class FreshCompilerTest(unittest.TestCase):
    def test_real_compiler_provider_and_relocation_rejection(self):
        import hashlib
        import shutil
        import source_providers as providers
        if not shutil.which('clang'):
            self.skipTest('clang unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'provider.c'
            source.write_text('unsigned answer(unsigned x) { return x + 42; }')
            unit = dict(source=str(source), argv=['clang','--target=arm-none-eabi',
                        '-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections'])
            functions, receipt = providers.compile_unit(unit,root/'first')
            body = next(f for f in functions if f['symbol']=='answer')
            region = dict(payload='g2-test',symbol='answer',start=0,end=body['size'],
                          sha256=hashlib.sha256(body['data']).hexdigest())
            plan = {'units':[dict(unit,regions=[region])]}
            selected, receipts = providers.build_selected(plan,root/'build',{'g2'})
            self.assertEqual(selected[0]['data'],body['data'])
            self.assertIn(str(source.resolve()),receipts[0]['inputs'])
            source.write_text('extern unsigned external(unsigned); unsigned answer(unsigned x) { return external(x); }')
            with self.assertRaises(ValueError):
                providers.build_selected(plan,root/'relocated',{'g2'})
            functions, _ = providers.compile_unit(unit,root/'call-object')
            function = next(f for f in functions if f['symbol']=='answer')
            data, _ = providers.link_function(root/'call-object/unit.o',function,0x1000,
                                               {'external':0x2001},root/'call-link')
            region.update(end=len(data),address=0x1000,bindings={'external':0x2001},
                          sha256=hashlib.sha256(data).hexdigest())
            selected, _ = providers.build_selected(plan,root/'bound',{'g2'})
            self.assertEqual(selected[0]['data'],data)
            data2,_=providers.link_function(root/'call-object/unit.o',function,0x3000,{'external':0x2001},root/'second-address')
            region2=dict(region,start=16,end=16+len(data2),address=0x3000,sha256=hashlib.sha256(data2).hexdigest())
            plan['units'][0]['regions']=[region,region2]
            placed,_=providers.build_selected(plan,root/'two-placements',{'g2'})
            self.assertNotEqual(placed[0]['file'],placed[1]['file'])
            for provider in placed:self.assertEqual((root/'two-placements'/provider['file']).read_bytes(),provider['data'])
            plan['units'][0]['regions']=[region]
            region['bindings']={'external':0x3001}
            with self.assertRaises(ValueError):
                providers.build_selected(plan,root/'wrong-binding',{'g2'})


class CoverageTest(unittest.TestCase):
    def test_code_data_assembly_and_unknown_do_not_mix(self):
        from firmware_coverage import coverage
        source=dict(file='compiled.bin',instruction_origin='c',content_ranges=[
            dict(start=0,end=2,kind='code'),dict(start=2,end=4,kind='data')])
        payload=dict(payload='r1-application',file='fixture.bin',size=8,regions=[
            dict(start=0,end=4,size=4,owner='source-built',source_provider=source),
            dict(start=4,end=6,size=2,owner='resource-file'),
            dict(start=6,end=8,size=2,owner='binary-pull-through')])
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'fixture.bin').write_bytes(b'abcdefgh')
            result=coverage({'payloads':[payload]},Path(tmp))
            totals=result['summaries'][-1]['bytes']
            self.assertEqual(totals['c_compiled_executable'],2)
            self.assertEqual(totals['compiled_non_executable_data'],2)
            self.assertEqual(totals['pulled_non_executable_confirmed'],2)
            self.assertEqual(totals['pulled_unclassified'],2)
            self.assertEqual(sum(totals.values()),8)
            source.update(start=0,end=4)
            payload['regions']=[dict(start=0,end=2,size=2,owner='source-built',source_provider=source),
                dict(start=2,end=4,size=2,owner='source-built',source_provider=source),*payload['regions'][1:]]
            result=coverage({'payloads':[payload]},Path(tmp))
            self.assertEqual(result['summaries'][-1]['bytes']['compiled_non_executable_data'],2)
            source['instruction_origin']='assembly'
            result=coverage({'payloads':[payload]},Path(tmp))
            self.assertEqual(result['summaries'][-1]['bytes']['c_compiled_executable'],0)
            self.assertEqual(result['summaries'][-1]['bytes']['assembly_source_executable'],2)
            payload['regions'][1]['start']=1
            with self.assertRaises(ValueError):coverage({'payloads':[payload]},Path(tmp))


class UniqueMatchingTest(unittest.TestCase):
    def test_recovered_branches_require_unique_entry_and_full_link_equality(self):
        import shutil
        import source_providers as providers
        from match_compiled import match
        if not shutil.which('clang') or not shutil.which('arm-none-eabi-ld'):
            self.skipTest('ARM compile/link tools unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'call.c'
            source.write_text('extern unsigned leaf(unsigned); unsigned caller(unsigned x) { return leaf(x)+leaf(x+1); }')
            unit=dict(source=str(source),argv=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections'])
            functions,_=providers.compile_unit(unit,root/'compile')
            function=next(f for f in functions if f['symbol']=='caller')
            body,_=providers.link_function(root/'compile/unit.o',function,0x1020,{'leaf':0x1101},root/'link')
            stock=bytearray(0x400);stock[0x20:0x20+len(body)]=body
            result=match(function,stock,{0x20,0x100},0x1000)
            self.assertIsNotNone(result)
            self.assertEqual(result['bindings'],{'leaf':0x1101})
            rebuilt,_=providers.link_function(root/'compile/unit.o',function,result['address'],result['bindings'],root/'recovered')
            self.assertEqual(rebuilt,body)
            stock[0x220:0x220+len(body)]=body
            self.assertIsNone(match(function,stock,{0x20,0x100,0x220},0x1000))




class LicenseFreeTest(unittest.TestCase):
    def test_rejects_proprietary_and_unrestricted_commands(self):
        from compiler_mode import validate_license_free
        with self.assertRaises(ValueError):
            validate_license_free({'units':[{'argv':['iccarm']} ]})
        with self.assertRaises(ValueError):
            validate_license_free({'units':[]},{'arbitrary':{}})
        with self.assertRaises(ValueError):
            validate_license_free({'units':[{'argv':['python3','untrusted.py']} ]})

class RemainingClassificationTest(unittest.TestCase):
    def test_listing_bytes_must_match_and_wrong_base_rejected(self):
        from classify_remaining import decoded_spans
        text='0x00001000  7047  bx lr\n0x00001002  ffff  decoded\n'
        self.assertEqual(decoded_spans(text,b'\x70\x47\0\0',0x1000), ([(0,2)],1))
        self.assertEqual(decoded_spans(text,b'\x70\x47\0\0',0), ([],2))

class ImmutableDataProviderTest(unittest.TestCase):
    def test_const_data_is_consumed_and_writable_data_rejected(self):
        import hashlib
        import shutil
        import source_providers as providers
        if not shutil.which('clang'):self.skipTest('clang unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'calibration.c'
            source.write_text('const unsigned calibration[3]={3350,3622,4310};')
            unit=dict(source=str(source),argv=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-O2','-fdata-sections'])
            providers.compile_unit(unit,root/'qualify')
            symbol=next(s for s in providers.functions(root/'qualify/unit.o',include_objects=True) if s['symbol']=='calibration')
            region=dict(payload='r1-test',symbol='calibration',symbol_kind='data',start=0,end=12,sha256=hashlib.sha256(symbol['data']).hexdigest())
            unit['regions']=[region]
            selected,_=providers.build_selected({'units':[unit]},root/'production',{'r1'})
            self.assertEqual(selected[0]['data'],symbol['data'])
            self.assertEqual(selected[0]['content_ranges'],[dict(start=0,end=12,kind='data')])
            source.write_text('unsigned calibration[3]={3350,3622,4310};')
            with self.assertRaisesRegex(ValueError,'immutable'):
                providers.build_selected({'units':[unit]},root/'mutable',{'r1'})


class AnchoredPlacementTest(unittest.TestCase):
    def test_short_literal_binding_requires_named_entry_and_full_link(self):
        import shutil
        import source_providers as providers
        from match_compiled import match
        if not shutil.which('clang') or not shutil.which('arm-none-eabi-ld'):self.skipTest('ARM tools unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'getter.c'
            source.write_text('extern unsigned scalar; unsigned getter(void) { return scalar; }')
            unit=dict(source=str(source),argv=['clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Oz','-ffunction-sections'])
            functions,_=providers.compile_unit(unit,root/'compile')
            function=next(f for f in functions if f['symbol']=='getter')
            data,_=providers.link_function(root/'compile/unit.o',function,0x1000,{'scalar':0x20000000},root/'original')
            self.assertLess(len(data),16)
            self.assertIsNone(match(function,data,{0},0x1000))
            found=match(function,data,{0},0x1000,anchored_entry=0)
            self.assertEqual(found['bindings'],{'scalar':0x20000000})
            linked,_=providers.link_function(root/'compile/unit.o',function,found['address'],found['bindings'],root/'recovered')
            self.assertEqual(linked,data)
            self.assertIsNone(match(function,data,{2},0x1000,anchored_entry=0))
            damaged=bytes([data[0]^1])+data[1:]
            self.assertIsNone(match(function,damaged,{0},0x1000,anchored_entry=0))


if __name__ == '__main__':
    unittest.main()
