#!/usr/bin/env python
import sys
import fileinput
from optparse import OptionParser

from molecule import Molecule, Atom

def get_arguments(args=None):
    if args is None:
        args == sys.argv[1:]

    parser = OptionParser(usage="xyz2mol [options]",
                                                version="0.1",
                                                description="converts an xyz file to a DALTON mol-file")
    (options, args) = parser.parse_args(args)

    #if len(args) != 1:
    #    parser.print_help()
    #    sys.exit()

    return (options, args)
    
def parse_lines():
    isParsing = True
    mol = None
    line_counter = 0
    n_atoms = 0
    mol = Molecule("")
    title = ""
    datas = []
    for line in fileinput.input():
        data = line.split()
        if isParsing:
            line_counter += 1
            if line_counter == 1: n_atoms = int(data[0])
            if line_counter == 2: continue # title line
            if line_counter > 1:
                char = data[0]
                data = map(float, data[1:])
                atom = Atom(char, data[0], data[1], data[2])
                if mol is not None:
                    mol.addAtom(atom)
    #f.close()
    return mol

char2charge = {'H':1.0, 'C':6.0, 'N':7.0, 'O':8.0, 'S':16.0}

def tostr(mol):
    print "BASIS"
    print "3-21G"
    print "title line 1"
    print "title line 2"
    # group together atoms of different nuclear charge
    atom_types = []
    for atom in mol.atoms:
        if atom.char not in atom_types:
            atom_types.append(atom.char)

    print "AtomTypes=%i NoSymmetry Angstrom" % (len(atom_types))
    # collect atoms by their types
    for atom_type in atom_types:
        atoms = []
        for atom in mol.atoms:
            if atom_type == atom.char:
                atoms.append(atom)

        print "Charge=%.1f Atoms=%i" % (char2charge[atoms[0].char], len(atoms))
        for atom in atoms:
            print "%s %22.6f %12.6f %12.6f" % (atom.char, atom.x, atom.y, atom.z)

if __name__ == '__main__':
    (options,args) = get_arguments()
    mol = parse_lines()
    tostr(mol)
