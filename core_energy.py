#!/usr/bin/env python3
	
'''
############################################################################
# USAGE  :: python3 sys.argv[0] 
# Author :: Asif Iqbal
# DATED  :: 01/12/2020
# NB     :: POSCAR can be in Cartesian/Direct coordinates.
# Calculate the core energy of the screw dislocations
# by sampling different local chemical environment within a supercell
# by translating the atoms keeping the screw dislocation fixed.
############################################################################
'''

import numpy as np
import os, sys, random, subprocess, shutil
from ase import Atoms
import ase.io
from ase.io import write, read
from ase.io.vasp import write_vasp, read_vasp

def read_poscar():
	pos = []; kk = []; lattice = []; sum = 0; 
	file = open('POSCAR_perfect','r')
	firstline  = file.readline() # IGNORE first line comment
	alat = float( file.readline() )# scale
	Latvec1 = file.readline().split(); #print("{:9.6f} {:9.6f} {:9.6f}".format(float(Latvec1[0]),float(Latvec1[1]),float(Latvec1[2])))
	Latvec2 = file.readline().split(); #print("{:9.6f} {:9.6f} {:9.6f}".format(float(Latvec2[0]),float(Latvec2[1]),float(Latvec2[2])))
	Latvec3 = file.readline().split(); #print("{:9.6f} {:9.6f} {:9.6f}".format(float(Latvec3[0]),float(Latvec3[1]),float(Latvec3[2]))) 
	elementtype= file.readline(); #print ("{}".format(elementtype.split() ))
	atomtypes  = file.readline(); #print ("{}".format(atomtypes.split() ))
	Coordtype  = file.readline().split()
	if (Coordtype[0] == 'Direct' or Coordtype[0] == 'direct'): exit("First, Convert to Cartesian!")
	nat = [int(i) for i in atomtypes.split()]
	for i in nat: sum = sum + i; n_atoms = sum				
	for x in range(int(n_atoms)):
		coord = [ float(i) for i in file.readline().split() ]
		pos = pos + [coord]
	file.close()
	return n_atoms,pos,firstline,alat,Latvec1,Latvec2,Latvec3,elementtype,atomtypes,Coordtype

def write_result(i,j,cnt,firstline,alat,Latvec1,Latvec2,Latvec3,elementtype,atomtypes,pos,n_atoms):
	with open( "iniTMP_"+str(cnt).zfill(2), 'w') as fdat1:
		fdat1.write( "{}\n".format( "iniTMP_"+str(i)+'_'+str(j) ) ) # Comment line in POSCAR
		fdat1.write( "{:5f}\n".format(alat) )
		fdat1.write( "{:15.11f} {:15.11f} {:15.11f}\n".format(float(Latvec1[0]),float(Latvec1[1]),float(Latvec1[2])) )
		fdat1.write( "{:15.11f} {:15.11f} {:15.11f}\n".format(float(Latvec2[0]),float(Latvec2[1]),float(Latvec2[2])) )
		fdat1.write( "{:15.11f} {:15.11f} {:15.11f}\n".format(float(Latvec3[0]),float(Latvec3[1]),float(Latvec3[2])) )
		fdat1.write( "{:5s}".format(elementtype) )
		fdat1.write( "{:5s}".format(atomtypes) )
		fdat1.write( "{:5s}\n".format(Coordtype[0]) )

 		# Displace the cell in the "X" & "Y" direction.		
		for x in range(0, int(n_atoms), 1): 
			fdat1.write( "{:15.12f} {:15.12f} {:15.12f}\n".format(pos[x][0]+i,pos[x][1]+j,pos[x][2] ) )
	
# -------------------------------------- MAIN PROGRAM -------------------------------------- 
if __name__ == "__main__":
	n_atoms,pos,firstline,alat,Latvec1,Latvec2,Latvec3,elementtype,atomtypes,Coordtype = read_poscar();
	Ax = float(Latvec1[0]); 
	Ay = np.linalg.norm(Latvec2[1]); 
	cnt = 0; cx = 0; cy = 0
	b = 3.40/2 * np.linalg.norm([1,1,1]);
	print("SYSTEM={}, #_atoms={} b={}".format(elementtype.split(), n_atoms, b), end='\t\n' )
	
	for i in np.linspace(0, Ax, 21, endpoint=True):
		for j in np.linspace(0, Ay, 10, endpoint=True):
			write_result(i,j,cnt,firstline,alat,Latvec1,Latvec2,Latvec3,elementtype,atomtypes,pos,n_atoms)
			L = 'dis_'+'X'+str(cx).zfill(2)+"_"+'Y'+str(cy).zfill(2)+'_'+str(cnt).zfill(2)
			shutil.rmtree( L , ignore_errors=True) #overwrite a directory
			
			os.mkdir( L )
			# copy the files to the directory.
			subprocess.call(['cp','-r','iniTMP_'+str(cnt).zfill(2), L ], shell = False)
			subprocess.call(['cp','-r','INCAR', L ], shell = False)
			subprocess.call(['cp','-r','POTCAR', L ], shell = False)
			subprocess.call(['cp','-r','KPOINTS', L ], shell = False)
			subprocess.call(['cp','-r','job.sh', L ], shell = False)
			subprocess.call(['cp','-r','input_dislo.babel', L ], shell = False)
			
			# Enter the directory.		
			os.chdir( L )
			subprocess.call(['cp','-r','iniTMP_'+str(cnt).zfill(2), 'CONTCAR'], shell = False)
			subprocess.call(['dislo', 'input_dislo.babel'], shell = False)
			K = 'disFIN_'+'X'+str(cx).zfill(2)+"_"+'Y'+str(cy).zfill(2)+'_'+str(cnt).zfill(2)
			subprocess.call( ['cp','-r', 'POSCAR', K ], shell = False)		
			subprocess.call( ['cp','-r', K, '../iniTMP_'+str(cnt).zfill(2) ], shell = False)		
			os.chdir('../')		
			
			print ( "Ax,Ay= {:12.6f},{:12.6f} {:3d}".format( i,j, cnt ), end="\n" )
			cnt += 1
			cy  += 1
		cy = 0	# reset counter
		cx +=1
	print("DISPLACED FILES HAS BEEN GENERATED in the X=<112>, Y=<110> ... ")


			
	
	