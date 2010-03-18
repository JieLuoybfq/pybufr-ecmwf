#!/usr/bin/env python

#  #[ documentation
#
# This module implements a more pythonic interface layer
# around pybufr_ecmwf and is intended to make use of the BUFR
# file format easier and more intuitive for people used to python
# rather than fortran.
#
# Note about the use of the "#  #[" and "#  #]" comments:
#   these are folding marks for my favorite editor, emacs, combined with its
#   folding mode
#   (see http://www.emacswiki.org/emacs/FoldingMode for more details)
# Please do not remove them.
#
# For details on the revision history, refer to the log-notes in
# the mercurial revisioning system hosted at google code.
#
# Written by: J. de Kloe, KNMI (www.knmi.nl), Initial version 04-Feb-2010    
#
# License: GPL v2.
#  #]
#  #[ imported modules
import os
import sys
import glob
from pybufr_ecmwf import RawBUFRFile
from pybufr_ecmwf import ProgrammingError, NotYetImplementedError
#  #]

class Singleton(object):
    #  #[ explanation
    # this Singleton class is a modified version of the one
    # used by Guido van Rossum in his examples in his paper
    # "Unifying types and classes in Python 2.2", see:
    # http://www.python.org/download/releases/2.2.3/descrintro/
    # Its purpose is to have only one instance for each different
    # Descriptor reference number. If another instance is created with
    # the same reference number, this will actually just be a pointer
    # to the already existing instance, and not a totally new instance.
    # This way a huge amount of memory can be saved for large
    # BUFR templates/messages.
    #  #]
    #  #[
    def __new__(cls, *args, **kwds):
        #  #[
        #print "class Singleton: calling __new__"    
        if len(args)>0:
            # use the first arg, in case of Descriptors this is the
            # reference number, as key in the instance dict
            val = args[0]
        else:
            # note: since this __new__ is called with the same arguments
            # as the cls.__init__ method, use the name init in this message
            # to make more clear to the user where the problem is.
            print "ERROR: at least one arg expected in init function !"
            raise AttributeError
        
        # the next line returns None if __instance_dict__ does not yet exist
        id = cls.__dict__.get("__instance_dict__")
        if id is None:
            # create a new dict to hold the instances of this class
            # to allow only one instance for each int val used in init.
            # NOTE THAT THIS WILL BE A CLASS VARIABLE
            # NOT AN INSTANCE VARIABLE
            # so all instances of this class will use the same dict
            cls.__instance_dict__ = id = {}

        if id.has_key(val):
            # ok, we already had an instance for this value, so return
            # a pointer to it, but first check if the init parameters
            # are identical
            instance = id[val]
            instance.checkinit(*args, **kwds)
            return instance

        # no instance yet exists for this value, so create a new one
        cls.__instance_dict__[val] = instance = object.__new__(cls)
        #instance.init(*args, **kwds)
        return instance
    #  #]
    #def init(self, *args, **kwds):
        #  #[
        #print "class Singleton: calling init"
        #pass
        #  #]
    #  #]

class Descriptor(Singleton):
    #  #[
    def __init__(self,reference,name,unit,unit_scale,
                 unit_reference,data_width):
        #  #[
        self.reference      = reference      # descriptor code
        self.name           = name           # descriptive text
        self.unit           = unit           # unit text
        self.unit_scale     = unit_scale     # multiplicative factor of 10
        self.unit_reference = unit_reference # offset
        self.data_width     = data_width     # number of bits for storage
        #  #]
    def __str__(self):
        #  #[
        txt = "reference: ["+str(self.reference)+"] "+\
              "name: ["+self.name+"] "+\
              "unit: ["+self.unit+"] "+\
              "unit_scale: ["+str(self.unit_scale)+"] "+\
              "unit_reference: ["+str(self.unit_reference)+"] "+\
              "data_width: ["+str(self.data_width)+"] "
        return txt
        #  #]
    def checkinit(self,reference,name,unit,unit_scale,
                  unit_reference,data_width):
        #  #[
        assert(self.reference      == reference)
        assert(self.name           == name)
        assert(self.unit           == unit)
        assert(self.unit_scale     == unit_scale)
        assert(self.unit_reference == unit_reference)
        assert(self.data_width     == data_width)
        #  #]
    #  #]

# todo: look-up the possibilities in the documentation
class ModifiedDescriptor():
    #  #[
    # note: this cannot be subclassed from Descriptor, since the whole
    # point of modified descriptors is that you can have several with
    # the same descriptor code but with different properties.
    # Since Descriptor is itself a subclass of Singleton this would not
    # be possible, so just copy all items defined by the descriptor
    # to allow easy modification
    def __init__(self,descriptor):
        #  #[
        self.descriptor = descriptor
        self.list_of_modifications = []

        # these properties are copied from the input descriptor,
        # unless they are changed by a modification
        self.reference      = descriptor.reference  # descriptor code
        self.name           = descriptor.name       # descriptive text
        self.unit           = descriptor.unit       # unit text
        self.unit_scale     = descriptor.unit_scale # multiplicative factor of 10
        self.unit_reference = descriptor.unit_reference # offset
        self.data_width     = descriptor.data_width # number of bits for storage
        #  #]        
    def add_modification(self,modification):
        #  #[
        assert(isinstance(modification,ModificationCommand))
        self.list_of_modifications.append(modification)
        # todo: depending on the type of midification
        #       change the instance variables
        #  #]
    #  #]
    
# todo: look-up the possibilities in the documentation
class ModificationCommand(Descriptor):
    #  #[
    def __init__(self,reference):
        #  #[
        self.reference      = reference      # descriptor code
        # TODO: add more state variables depending on the type
        # of modification

        # extract xxyyy from the 2xxyyy format of the descriptor
        reference_text = "%6.6i" % reference
        self.xx =reference_text[1:3]
        self.yyy=reference_text[3:]
        #  #]
    def __str__(self):
        #  #[
        txt = "modification command reference: ["+str(self.reference)+"] "
        return txt
        #  #]
    def checkinit(self,reference):
        #  #[
        assert(self.reference      == reference)
        #  #]
    def is_modification_start(self):
        #  #[
        if self.xx=="01" or self.xx=="07":
            if self.yyy!="000":
                return True
            else:
                return False
        print "ERROR: handling this modification is not fully implemented yet:"
        print self
        raise NotYetImplementedError
        #  #]
    def is_modification_end(self):
        #  #[
        if self.xx=="01" or self.xx=="07":
            if self.yyy=="000":
                return True
            else:
                return False
        print "ERROR: handling this modification is not fully implemented yet:"
        print self
        raise NotYetImplementedError
        #  #]
    def check_matches(self,d):
        #  #[
        #print "end modification: ",str(self)
        #print "seems to match modification: ",str(d)
        # check whether a clear command mathches a change command
        if self.xx=="01" or self.xx=="07":
            if ((self.yyy=="000" and d.yyy!="000") or
                (d.yyy=="000" and self.yyy!="000")   ):
                if self.xx==d.xx:
                    return True
                else:
                    return False
            else:
                print "ERROR: modification start-and-end do not match !"
                print "problem in check_matches."
                print "end modification: ",str(self)
                print "seems to match modification: ",str(d)
                raise IOError
        else:
            print "ERROR: handling this modification is not fully implemented yet:"
            print self
            raise NotYetImplementedError
        #  #]

    # Modification commands are:
    # (see:BUFR reference manual, by Milan Dragosavac, 2007, p.20)
    # 201yyy change data width
    # 202yyy change scale
    # 203yyy change reference value
    # 204yyy add associated field
    # 205yyy signify character
    # 206yyy signify data width
    # 207yyy increase scale, ref.val. and data width
    # 207000 cancel change
    # 208yyy change with of CCITTIA5 field
    # 209yyy IEEE floating point representation
    # 221yyy data not present

    # (see:BUFR reference manual, by Milan Dragosavac, 1984, p.67-71)
    # 222000 quality information
    # 223000 substituted values operator
    # 223255 substituted value marker operator
    # 224000 first order statistical values follow
    # 224255 first order statistical values marker operator
    # 225000 difference statistical values follow
    # 225255 difference statistical values marker operator
    # 232000 replaced/retained values follow
    # 232255 replaced/retained values marker operator
    # 235000 cancel backward data reference
    # 236000 define backward reference bit map
    # 237000 use defined bit map
    # 237255 cancel 237000
    
    # (see:BUFR reference manual, by Milan Dragosavac, 2007, p.21)
    # 241yyy define event
    # 241255 cancel 241yyy
    # 242yyy define conditioning event
    # 242255 cancel 242yyy
    # 243yyy categorical forecast values follow
    # 243255 cancel 243yyy
    #  #]

# todo: look-up the possibilities in the documentation
class SpecialCommand(Descriptor):
    #  #[
    def __init__(self,reference):
        #  #[
        self.reference      = reference      # descriptor code
        # TODO: add more state variables depending on the type
        # of special
        #  #]
    def __str__(self):
        #  #[
        txt = "special command reference: ["+str(self.reference)+"] "
        return txt
        #  #]
    def checkinit(self,reference):
        #  #[
        assert(self.reference      == reference)
        #  #]
    #  ==>descriptor
    #  ==>special command

    # the commands described by a reference like 1xxyyy
    # are replication commands, defined like this:
    #def get_replication_code(num_descriptors,num_repeats):
    #    repl_factor = 100000 + num_descriptors*1000 + num_repeats
    #    # for example replicating 2 descriptors 25 times will be
    #    # encoded as: 102025
    #    # for delayed replication, set num_repeats to 0
    #    # then add the Delayed_Descr_Repl_Factor after this code
    #    return repl_factor
    #  #]

class Replicator(Descriptor):
    #  #[
    def __init__(self):
        pass
    def checkinit(self):
        pass
    #  ==>replication-count
    #  ==>list-of-descriptor-objects = []
    #  #]

class DelayedReplicator(Descriptor):
    #  #[
    def __init__(self):
        pass
    def checkinit(self):
        pass
    #  ==>maximum-replication-count = 4
    #  ==>actual-replication-count-list ] [1,2,3,4]
    #  ==>list-of-descriptor-objects = []
    #  #]

class CompositeDescriptor(Descriptor): #[table D entry]
    #  #[
    def __init__(self,reference,descriptor_list,comment):
        #  #[
        self.reference = reference
        self.descriptor_list = descriptor_list
        self.comment = comment
        #  #]
    def __str__(self):
        #  #[
        txt = "reference: ["+str(self.reference)+"] "+\
              "refers to: "+\
              ";".join(str(d.reference) for d in self.descriptor_list)
        return txt
        #  #]
    def checkinit(self,reference,descriptor_list,comment):
        #  #[
        assert(self.reference       == reference)
        assert(self.descriptor_list == descriptor_list)
        assert(self.comment         == comment)
        #  #]
    #  #]

class BufrTable:
    #  #[
    def __init__(self,
                 autolink_tablesdir="tmp_BUFR_TABLES",
                 tables_dir=None):
        #  #[
        self.table_B   = {} # dict of desciptor-objects
        self.table_D   = {} # dict of composite-descriptor-objects
        self.specials  = {} # dict of specials
        self.modifiers = {} # dict of modifiers

        self.autolink_tables=True
        if (tables_dir):
            # dont use autolinking if the user provided a tables dir
            self.autolink_tables=False

        # if self.autolink_tables is True, 
        # try to automatically make symbolic links to
        # BUFR tables provided by the ECMWF library for any new
        # BUFR table name that is requested by the decoder/encoder
        # in this directory
        self.autolink_tablesdir=autolink_tablesdir
        
        if (self.autolink_tablesdir):
            self.set_bufr_tables_dir(self.autolink_tablesdir)
        else:
            self.set_bufr_tables_dir(tables_dir)
        #  #]
    def set_bufr_tables_dir(self,tables_dir):
        #  #[
        self.tables_dir = tables_dir
        
        # make sure the BUFR tables can be found
        # also, force a slash at the end, otherwise the library fails
        # to find the tables
        e = os.environ
        e["BUFR_TABLES"] = self.tables_dir+os.path.sep
        #  #]
    def get_descr_object(self,reference):
        #  #[
        if self.table_B.has_key(reference):
            return self.table_B[reference]
        if self.table_D.has_key(reference):
            return self.table_D[reference]
        # get 1st digit
        f=int(reference/100000.)
        # note: the cases f==0 should already be part of table_B
        # and the cases f==3 should already be part of table_D
        if f==1:
            # this is a special code
            if self.specials.has_key(reference):
                return self.specials[reference]
            else:
                # this is a new special
                print "adding special: ",reference
                special = SpecialCommand(reference)
                self.specials[reference] = special
                return special
        if f==2:
            # this is a modifier
            if self.modifiers.has_key(reference):
                return self.modifiers[reference]
            else:
                # this is a new modifier
                print "adding modifier: ",reference
                modifier = ModificationCommand(reference)
                self.modifiers[reference] = modifier
                return modifier
            
        return None
        #  #]
    def load(self,file):
        #  #[

        # first see if the user specified a valid full path/file combination
        # and use it if it exists
        if os.path.exists(file):
            tablefile=file
        else:
            # if it does not exist, try to find it in the tables_dir
            tablefile= os.path.join(self.tables_dir,file)
            if not os.path.exists(tablefile):
                # if still not found, see if autolinking is on
                if (self.autolink_tables):
                    # if so, try to automatically get a symlink 
                    print "autolinking table file: ",file
                    self.autolinkbufrtablefile(file)
                
        #print "inspecting file: ",file
        #maxlen=0
        #for line in open(file,'rt'):
        #    l=line.replace('\r','').replace('\n','')
        #    if len(l)>maxlen:
        #        maxlen = len(l)
        #print "longest line is: ",maxlen

        (path,base) = os.path.split(tablefile)
        if base[0].upper()== 'B':
            self.load_B_table(tablefile)
        elif base[0].upper()== 'D':
            self.load_D_table(tablefile)
        else:
            print "ERROR: don;t know what table this is"
            print "(path,base) = ",(path,base)
            raise IOError
        #  #]
    def autolinkbufrtablefile(self,file):
        #  #[
        if not self.autolink_tables:
            print "programming error in autolinkbufrtablefile!!!"
            raise ProgrammingError
        
        # define our own location for storing (symlinks to) the BUFR tables
        if (not os.path.exists(self.tables_dir)):
            os.mkdir(self.tables_dir)
    
        # make the needed symlinks
        if os.path.exists("ecmwf_bufrtables"):
            ecmwf_bufr_tables_dir = "ecmwf_bufrtables"
        else:
            ecmwf_bufr_tables_dir = "../ecmwf_bufrtables"
            
        ecmwf_bufr_tables_dir = os.path.abspath(ecmwf_bufr_tables_dir)
        tables_dir = os.path.abspath(self.tables_dir)

        # algorithm: try the list B or D files one by one,
        # and remove a character from the name in every step.
        # Then try to find a match using glob. This should give
        # the filename that most closely matches the required one,
        pattern=file
        while (len(pattern)>1):
            pattern=pattern[:-1]
            print "trying pattern: ",os.path.join(ecmwf_bufr_tables_dir,pattern)+'*'
            matches = glob.glob(os.path.join(ecmwf_bufr_tables_dir,pattern)+'*')
            print "matches = ",matches
            print "len(matches) = ",len(matches)
            if len(matches)>0:
                source      = matches[0]
                destination = os.path.join(self.tables_dir,file)
                if (not os.path.exists(destination)):
                    print "making symlink from ",source,\
                          " to ",destination
                    os.symlink(source,destination)
                break

        #print "test stop"
        #sys.exit(1)
        #  #]
    def load_B_table(self,file):
        #  #[
        print "loading B table from file: ",file
        nr_of_ignored_problematic_entries = 0
        for (i,line) in enumerate(open(file,'rt')):
            success = True
            l=line.replace('\r','').replace('\n','')
            # example of the expected format (156 chars per line):
            # " 005001 LATITUDE (HIGH ACCURACY)                                         DEGREE                     5     -9000000  25 DEGREE                    5         7"
            if len(l)>=118:
                txt_reference       = l[0:8] # 8 characters
                txt_name            = l[8:73] # 64 characters
                txt_unit            = l[73:98] # 24 characters
                txt_unit_scale      = l[98:102] # 4 characters
                txt_unit_reference  = l[102:115] # 14 characters
                txt_data_width      = l[115:118] # 4 characters
                # sometimes additional info seems present, but
                # I don't know yet the definition used for that
                txt_additional_info = ''
                if len(l)>118:
                    txt_additional_info = l[118:]
            else:
                success = False
                nr_of_ignored_problematic_entries += 1
                print "ERROR: unexpected format in table B file..."
                print "linecount: ",i
                print "line: ["+l+"]"
                print "Line is too short, it should hold at least 118 characters"
                print "but seems to have only: ",len(l)," characters."
                #print "txt_reference       = ["+l[0:8]+"]"
                #print "txt_name            = ["+l[8:73]+"]"
                #print "txt_unit            = ["+l[73:98]+"]"
                #print "txt_unit_scale      = ["+l[98:102]+"]"
                #print "txt_unit_reference  = ["+l[102:115]+"]"
                #print "txt_data_width      = ["+l[115:118]+"]"
                print "You could report this to the creator of this table "+\
                      "since this should never happen."
                print "Ignoring this entry ....."

            if (success):
                try:
                    reference = int(txt_reference,10)
                    unit_scale = int(txt_unit_scale)
                    unit_reference = int(txt_unit_reference)
                    data_width = int(txt_data_width)
                    
                    # remove excess spaces from the string before storing
                    name = txt_name.strip()
                    unit = txt_unit.strip()
                    
                except:
                    success = False
                    nr_of_ignored_problematic_entries += 1
                    if (txt_name.strip()=="RESERVED"):
                        print "Ignoring a reserved entry: "+txt_reference
                    else:
                        print "ERROR: unexpected format in table B file..."
                        print "Could not convert one of the numeric fields to integer."
                        print "txt_reference       = ["+txt_reference+"]"
                        print "txt_unit_scale      = ["+txt_unit_scale+"]"
                        print "txt_unit_reference  = ["+txt_unit_reference+"]"
                        print "txt_data_width      = ["+txt_data_width+"]"
                        print "Ignoring this entry ....."

            if (success):
                # add descriptor object to the list
                b_descr = Descriptor(reference,name,unit,
                                     unit_scale,unit_reference,data_width)
                if not self.table_B.has_key(reference):
                    #print "adding descr. key ",reference
                    self.table_B[reference] = b_descr
                else:
                    print "ERROR: multiple table B descriptors with identical reference"
                    print "number found. This should never happen !!!"
                    print "problematic descriptor is: ",b_descr
                    print "Ignoring this entry ....."
                    nr_of_ignored_problematic_entries += 1

        print "-------------"
        if (nr_of_ignored_problematic_entries>0):
            print "nr_of_ignored_problematic_entries = ",\
                  nr_of_ignored_problematic_entries
        print "Loaded: ",len(self.table_B)," table B entries"
        print "-------------"
        #print "self.table_B[006001] = ",self.table_B[int('006001',10)]
        #print "-------------"

        #  #]
    def add_ref_to_descr_list(self,descriptor_list,reference,ref_reference,line_nr,
                              postpone,report_unhandled):
        #  #[
        # get object for ref_reference
        #print "trying descriptor ",ref_reference
        descr = self.get_descr_object(ref_reference)
        if (descr==None):
            postpone = True
            if report_unhandled:
                print "---"
                print "descriptor ",ref_reference," is never defined but is used by"
                print "D-table entry ",reference," (line ",line_nr,")"
                #print "postponing processing of this one"
        else:
            # add this object to the list
            #print "adding descriptor with ref: ",ref_reference
            descriptor_list.append(descr)

        return postpone
        #  #]
    def decode_blocks(self,report_unhandled=False):
        #  #[ decode table D blocks of lines
        handled_blocks = 0
        list_of_handled_blocks = []
        for bl in self.list_of_D_entry_lineblocks:
            #print "bl=",bl
            for (j,(i,l)) in enumerate(bl):
                #print j,"considering line ["+l+"]"
                parts = l[:18].split()
                if j==0: # startline
                    #print "is a start line"
                    reference     = int(parts[0],10)
                    count          = int(parts[1])
                    ref_reference = int(parts[2],10)
                    comment        = ''
                    postpone = False
                    descriptor_list = []
                    if len(l)>18:
                        comment = l[18:]
                else: # continuation_line:
                    #print "is a continuation line"
                    ref_reference = int(parts[0],10)
                    extra_comment  = ''
                    if len(l)>18:
                        # todo: check if the ref_reference is maybe a table-D
                        # entry without comment, and add the comment there in stead
                        extra_comment = l[18:]
                        if not (extra_comment.strip()==""):
                            print "WARNING: ignoring extra comment on continuation line: "
                            print "line: ["+l+"]"
                        
                #print descriptor_list,reference,\
                #      ref_reference, postpone,report_unhandled
                postpone = self.add_ref_to_descr_list(descriptor_list,reference,
                                                      ref_reference,i,
                                                      postpone,report_unhandled)
            if (not postpone):
                # all continuation lines have been processed so store the result.
                # first a safety check
                if len(descriptor_list)==count:
                    #print "************************storing result"
                    D_descr = CompositeDescriptor(reference,descriptor_list,
                                                  comment)
                    if not self.table_D.has_key(reference):
                        #print "adding descr. key ",reference
                        self.table_D[reference] = D_descr
                    else:
                        print "ERROR: multiple table D descriptors with identical reference"
                        print "number found. This should never happen !!!"
                        print "problematic descriptor is: ",D_descr
                        print "Please report this problem, together with"
                        print "a copy of the bufr table you tried to read."
                        print "Ignoring this entry for now....."
                else:
                    print "ERROR: unexpected format in table D file..."
                    print "problematic descriptor is: ",reference
                    print "linecount: ",i
                    print "line: ["+l+"]"
                    print "This D-table entry defines more descriptors than"
                    print "specified in the start line."
                    print "Please report this problem, together with"
                    print "a copy of the bufr table you tried to read."
                    print "len(descriptor_list) = ",len(descriptor_list)
                    print "count = ",count
                    if len(descriptor_list)<count:
                        raise IOError
                    else:
                        print "ignoring excess descriptors for now..."
                        #print "************************storing result"
                        D_descr = CompositeDescriptor(reference,descriptor_list,
                                                      comment)
                        if not self.table_D.has_key(reference):
                            #print "adding descr. key ",reference
                            self.table_D[reference] = D_descr
                        else:
                            print "ERROR: multiple table D descriptors with identical reference"
                            print "number found. This should never happen !!!"
                            print "problematic descriptor is: ",D_descr
                            print "Please report this problem, together with"
                            print "a copy of the bufr table you tried to read."
                            print "Ignoring this entry for now....."
                        
                # mark this block as done
                list_of_handled_blocks.append(bl)
                # count successfully handled blocks
                handled_blocks += 1

        # remove the processed blocks
        for bl in list_of_handled_blocks:
            self.list_of_D_entry_lineblocks.remove(bl)

        remaining_blocks = len(self.list_of_D_entry_lineblocks)
                
        return (handled_blocks,remaining_blocks)
        #  #]
    def load_D_table(self,file):
        #  #[
        print "loading D table from file: ",file

        # known problem:
        # the code stops with an error if a D-table entry is used before
        # it is defined, even if it is defined lateron in the same D-table
        # in the current example file, this happens for entry 301028
        # which is used on line 67, but only defined on line 69

        print "********************"
        print "**** first pass ****"
        print "********************"

        #  #[ create a list of blocks of lines
        self.list_of_D_entry_lineblocks = []
        this_lineblock = None
        for (i,line) in enumerate(open(file,'rt')):
            l=line.replace('\r','').replace('\n','')
            #print "considering line ["+l+"]"
            parts = l[:18].split()
            start_line = False
            continuation_line = False
            if (len(parts)==3):
                start_line = True
            elif (len(parts)==1):
                continuation_line = True
            else:
                print "ERROR: unexpected format in table D file..."
                print "linecount: ",i
                print "line: ["+l+"]"
                print "first 17 characters should hold either 1 or 3 integer"
                print "numbers, but in stead it holds: ",len(parts)," parts"
                print "You could report this to the creator of this table "+\
                      "since this should never happen."
                raise IOError
            
            if start_line:
                #print "is a start line"
                if (this_lineblock != None):
                    # save the just read block in the list
                    self.list_of_D_entry_lineblocks.append(this_lineblock)
                # and start with a new lineblock
                this_lineblock = []
                this_lineblock.append((i,l))
                
            if continuation_line:
                #print "is a continuation line"
                this_lineblock.append((i,l))

        # save the last block as well
        if (this_lineblock != None):
            # save the final block in the list
            self.list_of_D_entry_lineblocks.append(this_lineblock)

        self.num_D_blocks = len(self.list_of_D_entry_lineblocks)
        #  #]

        print "*********************"
        print "**** second pass ****"
        print "*********************"

        handled_blocks = 1
        loop_count = 0
        while (handled_blocks>0):
            loop_count += 1
            print "==============>loop count: ",loop_count
            (handled_blocks,remaining_blocks) = self.decode_blocks()

        print "remaining blocks: ",remaining_blocks
        print "decoded blocks:   ",handled_blocks
        if remaining_blocks>0:
            print "---------------------------------------------------"
            print "Reporting problematic blocks:"
            print "---------------------------------------------------"
            (handled_blocks,remaining_blocks) = \
                           self.decode_blocks(report_unhandled=True)
            print "---------------------------------------------------"

        print "self.num_D_blocks = ",self.num_D_blocks
        print "remaining_blocks = ",remaining_blocks

        if (self.num_D_blocks==remaining_blocks):
            print "ERROR: it seems you forgot to load the B-table before trying"
            print "to load the D-table. It is required to load the corresponding B-table"
            print "first, because it is needed to apply consistency checking on the"
            print "D-table during the read process."
            raise ProgrammingError

        #print "test stop"
        #sys.exit(0)
        #  #]
    def apply_special_commands(self):
        #  #[
        # application of special commands (i.e. replications) is
        # done by calling the buxdes subroutine in the ECMWF library
        # so for now I won't implement this in python
        pass
        #  #]
    def apply_modification_commands(self,descr_list):
        #  #[
        # register each modification with all the descriptors that
        # it applies to. This is needed to allow calculation of the
        # allowed range of the value of the descriptor, which is something
        # I would like to be able to check from within python
        # (because the errors thrown by the ECMWF BUFR library can be rather
        # difficult to decipher, and usually won't point you to the mistake
        # that you probably made in your own program).

        # input: an expanded descriptor list

        # output: a new descriptor list, with descriptors that need to be
        # modified replaced by their corresponding ModifiedDescriptor
        # instance, which should hold pointers to the original descriptor
        # and to all modifications applied to it

        mod_descr_list = []
        current_modifications = []
        for d in descr_list:
            if isinstance(d,ModificationCommand):
                if d.is_modification_start():
                    current_modifications.append(d)
                elif d.is_modification_end():
                    removed_d = current_modifications.pop()
                    d.check_matches(removed_d)
                else:
                    print "Problem in apply_modification_commands."
                    print "Modifier not recognised as start or end command."
                    print "This should never happen !"
                    raise ProgrammingError
            elif isinstance(d,SpecialCommand):
                print "Problem in apply_modification_commands."
                print "The current descriptor list still seems to contain"
                print "replication commands, so it is not yet expanded!!!"
                print "The input to apply_modification_commands() should be"
                print "an expanded descriptor list..."
                raise ProgrammingError
            else:
                if len(current_modifications)>0:
                    mod_descr = ModifiedDescriptor(d)
                    print "current_modifications:"
                    print ";".join(str(m) for m in current_modifications)
                    for m in current_modifications:
                        mod_descr.add_modification(m)
                    mod_descr_list.append(mod_descr)
                else:
                    mod_descr_list.append(d)
        return mod_descr_list
        #  #]
    #  possible additional methods:
    #  ==>write-tables
    #  #]
    
class DataValue:
    #  #[
    pass
    #  ==>value or string-value
    #  ==>already filled or not?
    #  ==>pointer to the associated descriptor object
    #  #]

class BUFRMessage: # [moved here from pybufr_ecmwf.py]
    #  #[
    pass
    #  ==>properties-list = [sec0,sec1,sec2,sec3 data]
    #  ==>list-of-descriptor-objects = []
    #  ==>finish (set num subsets, num delayed replications)
    #  ==>2D-data-array of data objects (num subsets x expanded num descriptors)
    #
    # possible methods:
    # -add_descriptor
    # -expand_descriptorList
    # -encode
    # -decode
    # -print_sections_012
    # -get_descriptor_properties
    # -fill_one_real_value
    # -fill_one_string_value
    # -get_one_real_value
    # -get_one_string_value
    # -...
    #  #]

class BUFRFile(RawBUFRFile):
    #  #[
    pass
    # bufr-file [can reuse much functionality from what I have now in the
    #            RawBUFRFile class in pybufr_ecmwf.py]
    #  ==>some meta data
    #  ==>list-of-bufr-msgs = []
    #  #]

if __name__ == "__main__":
        #  #[ test program
        print "Starting test program:"
        BT = BufrTable(autolink_tablesdir="tmp_BUFR_TABLES")
        # load BUFR tables using the automatically linked
        # tables defined on the lines above

        # test the available bufr tables
        #table_codes = ["0000000000000014000","0000000000098000000",
        #               "0000000000098002001","0000000000098006000",
        #               "0000000000098006001","0000000000098013001",
        #               "0000000000098014001","0000000000254011001"]
        #for table_code in table_codes:
        #    BT.load("B"+table_code+".TXT")
        #    BT.load("D"+table_code+".TXT")

        # test application of modification commands:
        # this is D-descriptor 331004

        # load the ADM-Aeolus L2B-product BUFR table
        path="alt_bufr_tables"
        table_code="0000000000098015001"
        BT.load(os.path.join(path,"B"+table_code+".TXT"))
        BT.load(os.path.join(path,"D"+table_code+".TXT"))

        codes = ["207001", # = modifier
                 "005001", # = LATITUDE (HIGH ACCURACY)  [DEGREE]
                 "006001", # = LONGITUDE (HIGH ACCURACY) [DEGREE]
                 "207000"] # = end of modifier   
        descr_list = []
        for c in codes:
            descr_list.append(BT.get_descr_object(int(c,10)))
        print "descr_list = ",descr_list
        
        mod_descr_list = BT.apply_modification_commands(descr_list)

        # this is how I the BUFR module interfacing should look like

        # get a msg instance
        bm = BUFRMessage()
        # all sections should be filled with sensible defaults but ofcourse
        # the user should be able to change all of them
        # also the user should be able to insert a bufr table name to be
        # used, in contrast with the ECMWF method of using the metadata
        # to construct the BUFR table name. In that case the symbolic link
        # to the constructed BUFR table name should be rerouted to the name
        # provided by the user, to trick the ECMWF library in using it.

        # built the template
        #bm.add_descriptor()
        #bm.add_descriptor()
        #bm.add_descriptor()

        # expand any D-table entries
        #bm.expand_descriptor_list()

        #ns=361
        #bm.set_num_subsets(ns)
        #for ss in range(ns):
        #    bm.set_fill_index_to_start_subset(ss)
        #    bm.fill_one_element(val,descr_code,descr_text)
        #    bm.fill_one_element(val,descr_code,descr_text)
        #    bm.fill_one_element(val,descr_code,descr_text)

        #bf=BUFRFile()
        #bf.open(file='',mode='w')
        #bf.write(bm) # this should automatically do the encoding
        #bf.close()

        # further ideas:
        # -allow generation of a custom minimal BUFR table
        #  holding only the entries needed to decode/encode the
        #  current BUFR message
        # -add methods to compose a BUFR table from scratch
        #  and/or modify it (add, delete, save, load)
        #
        #  #]
