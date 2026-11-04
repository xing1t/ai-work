"""Read-only offline archive checks. Python standard library; no network or EDA."""
from pathlib import Path
from urllib.parse import unquote
import collections
import hashlib
import json
import re
import subprocess

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    errors = []
    archive = json.loads((PROJECT / 'validation/archive-map.json').read_text(encoding='utf-8'))
    copied = [x for x in archive['entries'] if x['repository_path']]
    for entry in copied:
        target = REPO / entry['repository_path']
        if not target.is_file() or digest(target.read_bytes()) != entry['copied_sha256']:
            errors.append('Copied hash mismatch: ' + entry['repository_path'])
        if entry['manifest_sha256'] and entry['manifest_sha256'] != entry['copied_sha256']:
            errors.append('Manifest hash mismatch: ' + entry['repository_path'])

    source = (PROJECT / 'hardware/pcb/PCB3_final_source.txt').read_bytes()
    final = json.loads((PROJECT / 'validation/PCB3_final_verified.json').read_text(encoding='utf-8'))['result']
    initial = json.loads((PROJECT / 'validation/pcb_pads_initial.json').read_text(encoding='utf-8'))['result']
    embedded = final['source'].encode('utf-8')
    if source.replace(b'\r\n', b'\n') != embedded.replace(b'\r\n', b'\n'):
        errors.append('Source differs beyond CRLF/LF')
    fingerprint = lambda ps: collections.Counter((p['ref'], q['n'], q['net']) for p in ps for q in p['pads'])
    if fingerprint(initial) != fingerprint(final['parts']):
        errors.append('PCB pad fingerprint changed')
    records = []
    for line in final['source'].splitlines():
        header, data = line.split('||')
        records.append((json.loads(header), json.loads(data.rstrip('|'))))
    counts = {
        'parts': len(final['parts']),
        'nonempty_nets': len({q['net'] for p in final['parts'] for q in p['pads'] if q['net']}),
        'pad_entries': sum(len(p['pads']) for p in final['parts']),
        'copper_segments': sum(h['type'] == 'LINE' and d.get('layerId') in [1, 2] for h, d in records),
        'vias': sum(h['type'] == 'VIA' for h, d in records),
        'fills': sum(h['type'] == 'FILL' for h, d in records),
    }
    if counts != dict(parts=56, nonempty_nets=41, pad_entries=191, copper_segments=638, vias=51, fills=2):
        errors.append('Unexpected PCB counts')
    if not (final['drcPassed'] is True and final['drc'] == [] and final['saved'] is True):
        errors.append('Snapshot DRC/save fields do not support conclusion')
    if len(final['references']) != 56 or not all(r['visible'] for r in final['references']):
        errors.append('References not all visible')
    if any(d['netName'] != 'GND' for h, d in records if h['type'] == 'FILL'):
        errors.append('Unexpected fill network')

    schematic = json.loads((PROJECT / 'hardware/schematic/eda_final.json').read_text(encoding='utf-8'))['result']
    netlist = json.loads(schematic['netlist'])
    pins = {c['props']['Designator'] + '.' + str(n): p['net'] for c in netlist['components'].values() for n, p in c['pinInfoMap'].items()}
    expected = json.loads((PROJECT / 'validation/eda_connections.json').read_text(encoding='utf-8'))
    bad_pins = [k for k, v in expected.items() if pins.get(k) != v]
    if len(expected) != 173 or bad_pins or len(schematic['parts']) != 56 or schematic['saved'] is not True:
        errors.append('Schematic readback mismatch')
    documented = json.loads((PROJECT / 'validation/offline-evidence-check.json').read_text(encoding='utf-8'))
    if documented['counts'] != counts or documented['source_file_sha256'] != digest(source) or documented['source_embedded_utf8_sha256'] != digest(embedded):
        errors.append('Offline report differs from evidence')
    readme = (PROJECT / 'README.md').read_text(encoding='utf-8')
    for phrase in ['56', '41', '191', '638', '51', 'DRC=false', '固定 FILL', '未验证', '173', 'CRLF']:
        if phrase not in readme:
            errors.append('README lacks evidence/limit: ' + phrase)

    files = [p for p in REPO.rglob('*') if p.is_file() and '.git' not in p.relative_to(REPO).parts]
    forbidden_parts = {'node_modules', '__pycache__', 'private', 'secrets', 'credentials', 'src'}
    forbidden_suffixes = {'.pdf', '.jar', '.exe', '.msi', '.log', '.pem', '.key', '.p12', '.pfx', '.zip', '.7z'}
    # Values only: report paths, never secret text. Documentation mentions are not values.
    secret_patterns = [
        rb'gh[pousr]_[A-Za-z0-9]{30,}',
        rb'github_pat_[A-Za-z0-9_]{40,}',
        rb'sk-[A-Za-z0-9_-]{24,}',
        rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
        rb'(?i)(?:authorization\s*[:=]\s*[\x22\x27]?bearer\s+)[A-Za-z0-9_.-]{16,}',
        rb'(?i)(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[\x22\x27]?\s*[:=]\s*[\x22\x27][A-Za-z0-9_/+=.-]{16,}[\x22\x27]',
    ]
    checked_links = 0
    for path in files:
        rel = path.relative_to(REPO)
        if any(part in forbidden_parts for part in rel.parts) or path.suffix.lower() in forbidden_suffixes or path.name.startswith('.env') or path.name in {'package.json', 'package-lock.json'}:
            errors.append('Excluded file: ' + rel.as_posix())
        data = path.read_bytes()
        if any(re.search(pattern, data) for pattern in secret_patterns):
            errors.append('Potential credential: ' + rel.as_posix())
        if path.suffix == '.md':
            text = data.decode('utf-8-sig')
            # Markdown links only; historical raw C: paths and bare URLs are provenance.
            for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', text):
                target = target.strip('<>')
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                    continue
                target = unquote(target.split('#')[0])
                if target:
                    checked_links += 1
                    if not (path.parent / target).exists():
                        errors.append('Broken relative link: ' + rel.as_posix() + ' -> ' + target)

    staged = []
    index_check = 'not available'
    if (REPO / '.git').is_dir():
        result = subprocess.run(['git', '-C', str(REPO), 'diff', '--cached', '--name-only', '-z'], capture_output=True, check=True)
        staged = [x.decode('utf-8') for x in result.stdout.split(b'\0') if x]
        for name in staged:
            target = REPO / name
            data = subprocess.run(['git', '-C', str(REPO), 'show', ':' + name], capture_output=True, check=True).stdout
            if not target.is_file() or data != target.read_bytes():
                errors.append('Index/worktree byte mismatch: ' + name)
        index_check = 'passed' if staged else 'empty'
    report = {'mode': 'read-only offline; no EDA, no network', 'copied_originals_checked': len(copied), 'working_files': len(files), 'working_bytes': sum(p.stat().st_size for p in files), 'relative_links_checked': checked_links, 'pcb_counts': counts, 'schematic_connections_checked': len(expected), 'schematic_mismatches': len(bad_pins), 'source_byte_equal': source == embedded, 'source_CRLF_LF_normalized_equal': True, 'staged_files': len(staged), 'index_bytes_check': index_check, 'credential_scan': 'known token/private-key and assigned-secret patterns; no matches' if not any('credential' in e for e in errors) else 'review required', 'errors': errors, 'passed': not errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
