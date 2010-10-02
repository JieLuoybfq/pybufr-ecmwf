#!/usr/bin/env python

"""
This is a small tool/example program intended to loop over all bufr messages
in a bufr file and extract all the data from it, which is then printed
to stdout.
"""

# For details on the revision history, refer to the log-notes in
# the mercurial revisioning system hosted at google code.
#
# Written by: J. de Kloe, KNMI, Initial version 24-Sep-2010    
#
# License: GPL v2.

#  #[ imported modules
import os, sys # operating system functions
import numpy   # array functionality

# import the python file defining the RawBUFRFile class
from pybufr_ecmwf.bufr import BUFRReader
from pybufr_ecmwf.raw_bufr_file import RawBUFRFile
from pybufr_ecmwf.bufr_interface_ecmwf import BUFRInterfaceECMWF

#  #]

def print_bufr_content(input_bufr_file):
    #  #[ implementation 1
    
    # get an instance of the BUFR class
    # which automatically opens the file for reading and decodes it
    bob = BUFRReader(input_bufr_file)
    
    for msg_nr in range(1,bob.num_msgs+1):
        bob.get_next_msg()
        data = bob.get_values_as_2d_array()
        for subs in range(len(data[:,0])):
            print str(subs)+' '+' '.join(str(val) for val in data[subs,:])
        
    # close the file
    bob.close()
    #  #]

def print_bufr_content2(input_bufr_file):
    #  #[ implementation 2
    
    # get an instance of the BUFR class
    # which automatically opens the file for reading and decodes it
    bob = BUFRReader(input_bufr_file)
    
    for msg_nr in range(1,bob.num_msgs+1):
        bob.get_next_msg()
        
        nsubsets = bob.get_num_subsets()
        for subs in range(nsubsets):
            nelements = bob.get_num_elements()
            data_list = []
            for descr_nr in range(nelements):
                data = bob.get_value(descr_nr,subs)
                data_list.append(data)
            print str(subs)+' '+' '.join(str(val) for val in data_list)
        
    # close the file
    bob.close()
    #  #]

def print_bufr_content3(input_bufr_file):
    #  #[ implementation 3

    # get an instance of the RawBUFRFile class
    BF = RawBUFRFile()
    
    # open the file for reading, count nr of BUFR messages in it
    # and store its content in memory, together with
    # an array of pointers to the start and end of each BUFR message
    BF.open(input_bufr_file, 'r')
    
    # extract the number of BUFR messages from the file
    num_msgs = BF.get_num_bufr_msgs()

    for msg_nr in range(1,num_msgs+1):
        raw_msg = BF.get_raw_bufr_msg(msg_nr)
        bufr_obj = BUFRInterfaceECMWF(encoded_message=raw_msg,
                                      max_nr_expanded_descriptors=44)
        bufr_obj.decode_sections_012()
        bufr_obj.setup_tables()
        bufr_obj.decode_data()

        nsubsets = bufr_obj.get_num_subsets()
        for subs in range(nsubsets):
            nelements = bufr_obj.get_num_elements()
            data_list = []
            for descr_nr in range(nelements):
                data = bufr_obj.get_value(descr_nr,subs)
                data_list.append(data)
            print str(subs)+' '+' '.join(str(val) for val in data_list)
        
    # close the file
    BF.close()
    #  #]

#  #[ run the tool
if len(sys.argv)<2:
    print 'please give a BUFR file as argument'
    sys.exit(1)

input_bufr_file  = sys.argv[1]

print_bufr_content(input_bufr_file)
#  #]