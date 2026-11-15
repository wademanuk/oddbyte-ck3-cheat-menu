"""Small lossless-value parser for the installed game's declarative script blocks."""
from dataclasses import dataclass
import re

TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|#[^\r\n]*|\?=|>=|<=|!=|[{}=<>]|[^\s{}=<>!?#]+')

@dataclass
class Entry:
    key: str
    op: str = ''
    value: object = None

def parse(text):
    tokens=[m.group() for m in TOKEN.finditer(text.lstrip('\ufeff')) if not m.group().startswith('#')]
    pos=0
    def block(nested=False):
        nonlocal pos
        out=[]
        while pos<len(tokens):
            key=tokens[pos];pos+=1
            if key=='}':
                if not nested:raise ValueError('Unexpected closing brace')
                return out
            # Native faith definitions include lists of anonymous blocks (holy-order names).
            if key=='{':
                out.append(Entry('', '', block(True)))
                continue
            if pos<len(tokens) and tokens[pos] in ['=','?=','>=','<=','!=','>','<']:
                op=tokens[pos];pos+=1
                if pos>=len(tokens):raise ValueError('Missing value for '+key)
                value=tokens[pos];pos+=1
                if value=='{':value=block(True)
                elif value=='}':raise ValueError('Missing value for '+key)
                out.append(Entry(key,op,value))
            else:out.append(Entry(key))
        if nested:raise ValueError('Unclosed block')
        return out
    return block()

def dump(entries,indent=0):
    lines=[]
    for e in entries:
        prefix='    '*indent+e.key
        if not e.key and isinstance(e.value,list):
            lines.append('    '*indent+'{')
            lines.append(dump(e.value,indent+1))
            lines.append('    '*indent+'}')
        elif not e.op:lines.append(prefix)
        elif isinstance(e.value,list):
            lines.append(prefix+' '+e.op+' {')
            lines.append(dump(e.value,indent+1))
            lines.append('    '*indent+'}')
        else:lines.append(prefix+' '+e.op+' '+e.value)
    return '\n'.join(lines)

def get(entries,key,default=None):
    return next((e.value for e in entries if e.key==key),default)

def walk(entries):
    for e in entries:
        yield e
        if isinstance(e.value,list):yield from walk(e.value)
