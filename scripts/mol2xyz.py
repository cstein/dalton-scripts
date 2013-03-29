#!/usr/bin/env python
import sys
import fileinput

from molecule import Molecule, Atom

atoms = []

def getint(value):
    # assume '=' delitimer
    data = value.split('=')
    return int(data[1])

def getfloat(value):
    # assume '=' delitimer
    data = value.split('=')
    return float(data[1])

def getbool(value):
    return True

keywords = {'atomtypes' :getint,
                        'nosymmetry':getbool,
                        'angstrom'    :getbool}
atoms = {'charge':getfloat,
                 'atoms':getint}

values = {}

def parse_keyword_line(line):
    data = line.split()
    for item in data:
        litem = item.lower()
        # loop through all keys
        for key in keywords.keys():
            if key in litem:
                values[key] = keywords[key](litem)

def parse_atom_line(line):
    atom_values = {}
    data = line.split()
    for item in data:
        litem = item.lower()
        # loop through all keys
        for key in atoms.keys():
            if key in litem:
                atom_values[key] = atoms[key](litem)

    return atom_values

def read_atoms():
    #f = open(filename,'r')

    line_count = 0
    nat = 0
    mol = Molecule("")
    #for line in f:
    for line in fileinput.input():
        line_count += 1
        if line_count == 3: values['title'] = line[:-1]
        uline = line.upper()
        if 'ATOMTYPES' in uline:
            parse_keyword_line(line)

        if 'CHARGE' in uline:
            atom_values = parse_atom_line(line)
            nat = atom_values['atoms']
            continue

        if nat > 0:
            nat -= 1
            data = line.split()
            char = data[0]
            data = map(float, data[1:])
            atom = Atom(char, data[0], data[1], data[2])
            mol.addAtom(atom)

    #f.close()
    return mol


if __name__ == '__main__':
    mol = read_atoms()
    print mol
