#!/usr/bin/env python
import sys
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='converts an xyz file to a DALTON mol-file', prog="xyz2mol", usage="xyz2mol <xyzfile> [options]")
    parser.add_argument('--version', action='version', version='%(prog)s 0.2')
    parser.add_argument('input', help="XYZ filename.",type=argparse.FileType('r'))
    parser.add_argument('-b', '--basis', help='Basis Set. Default is 3-21G', action='store', default="3-21G")
    parser.add_argument('-f', '--firsttitle', help='First title line', action='store', default="title line 1")
    parser.add_argument('-s', '--secondtitle', help='Second title line', action='store', default="title line 2")
    parser.add_argument('-c', '--charge', help='Charge of the molecule. Default is 0', action='store', default=0, type=int)

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args

    
def parse_lines():
    isParsing = True
    mol = None
    line_counter = 0
    n_atoms = 0
    mol = Molecule("")
    title = ""
    datas = []
    for line in args.input:
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
    return mol

class Molecule:
  def __init__(self, title):
    self.title = title
    self.atoms = []

  def addAtom(self, atom):
    self.atoms.append(atom)

  def __str__(self):
    s = "%i\n%s\n" % (len(self.atoms), self.title)
    temp = "\n".join(str(atom) for atom in self.atoms)
    return "%s%s" % (s, temp)

class Atom:
  def __init__(self,char,x,y,z):
    self.char = char
    self.x = x
    self.y = y
    self.z = z

  def __str__(self):
    return "%s %20.12f %20.12f %20.12f" % (self.char, self.x, self.y, self.z)

char2charge = {'H':1.0, 'C':6.0, 'N':7.0, 'O':8.0, 'S':16.0}

def tostr(mol,args):
    print "BASIS"
    print args.basis
    print args.firsttitle
    print args.secondtitle
    # group together atoms of different nuclear charge
    atom_types = []
    for atom in mol.atoms:
        if atom.char not in atom_types:
            atom_types.append(atom.char)

    print "AtomTypes=%i Charge=%i NoSymmetry Angstrom" % (len(atom_types), args.charge)
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
    args = parse_arguments()
    mol = parse_lines()
    tostr(mol,args)
