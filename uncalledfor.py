#!/usr/bin/env python

import re
import subprocess
import sys


class Function:
    def __init__(self, name, calls):
        self.name = name
        self.calls = calls
        self.called = False

    def __str__(self):
        return f"{self.name}: {self.calls}"

    def call(self):
        self.called = True

    def is_called(self):
        return self.called


def parse(section):
    lines = section.split("\n")
    if len(lines) <= 1:
        return None
    # 0000000000001ed0 <_nss_MkConfigString>:
    name_match = re.search(r"[0-9a-f]{16} <([A-Za-z0-9_]+)>:", lines[0])
    if not name_match:
        return None
    name = name_match.group(1)
    # 56ba4: 94000052     	bl	0x56cec <_PK11_DestroyGenericObject>
    # call_re = r"\s+[0-9a-f]+: [0-9]+\s+[a-z]+\s+0x[0-9a-f]+ <([A-Za-z0-9_]+)>"
    call_re = r".*<([A-Za-z0-9_]+)>$"
    calls = set()
    for line in lines[1:]:
        call_match = re.search(call_re, line)
        if call_match:
            calls.add(call_match.group(1))
    return Function(name, calls)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: uncalledfor.py <library>", file=sys.stderr)
        sys.exit(1)
    nm = subprocess.run(
        ["nm", "-g", "--defined-only", sys.argv[1]],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    public_functions = set()
    for line in nm.stdout.split("\n"):
        # 0000000000011c30 T _CERT_CacheOCSPResponseFromSideChannel
        public_function_match = re.search("[0-9a-f]{16} T ([A-Za-z0-9_]+)", line)
        if public_function_match:
            public_functions.add(public_function_match.group(1))
    objdump = subprocess.run(
        ["objdump", "-d", sys.argv[1]],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    functions = filter(
        lambda f: f != None,
        [parse(section) for section in objdump.stdout.split("\n\n")],
    )
    function_map = {function.name: function for function in functions}
    for name, function in function_map.items():
        for call in function.calls:
            if call in function_map:
                function_map[call].call()
    for function in function_map.values():
        if not function.is_called() and function.name not in public_functions:
            print(function.name)
