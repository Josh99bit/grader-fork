import os
import subprocess
import time
from threading import Thread

class Grader:


  def __init__ (self):
    self.codefile = "code.py" # default file containing code
    self.codeout = "tmp"      # temp output file from code
    self.folder = ""          # folder of files
    self.ifile = ""           # specific testcase. If "", all testcases will be used.
    self.ifilelist = []       # list of test case input files
    self.ofilelist = []       # list of test case output files
    self.maxlen = 0           # max filename length for display purpose
    self.timelimit = 10       # time limit for code execution
    self.timestart = 0        # time lapse start 
    self.timeron = False      # timer on/off


  # start timer
  def start_timer(self):
    self.timestart = time.time()
    self.timeron = True


  # end timer
  def end_timer(self):
    self.timeron = False


  # return time lapse
  def time_lapse(self):
    return round(time.time() - self.timestart, 2)


  # timer
  def timer(self):
    while True:
      if self.timeron:
        if self.time_lapse() > self.timelimit:
          print("time exceeded...", end="", flush=True)
          self.timeron = False
      else:
        break
  
  # code files cleanup
  def cleanup(self):

    directories = os.listdir()
    for folder in directories:
      try:
        filelist = os.listdir(folder)
        if self.codefile in filelist:
          with open(folder+"/"+self.codefile, "w") as f1:
            f1.write("")
        if self.codefile in filelist:   
          with open(folder+"/"+self.codeout, "w") as f2:
            f2.write("")
      except:
        pass


  # read list of input and output files. 
  # Return: True - successful / False - unsuccessful
  def read_file_lists(self):

    # read lists
    self.ifilelist = []
    self.ofilelist = []
    files = os.listdir(self.folder)
    for name in files:
      if ".in" in name:
        self.ifilelist.append(name)  
      elif ".out" in name:
        self.ofilelist.append(name)
        self.maxlen = max(len(name), self.maxlen)
    self.ifilelist.sort()
    self.ofilelist.sort()

    # check missing files
    if len(self.ifilelist) == 0:
      print("Missing test case files in folder")
      return False

    # check list integrity
    else:
      for i in range(len(self.ifilelist)):
        check = self.ifilelist[i][0:-2] + "out"
        if check != self.ofilelist[i]:
          print("Mismatch input and output file", self.ifilelist[i], self.ofilelist[i])
          return False
      return True


  # compare code output with test case output
  # Return: True - all correct / False - error
  def match(self, index):

    # run match
    with open(self.folder+"/"+self.ofilelist[index], "r") as fans:
      with open(self.folder+"/"+self.codeout, "r") as fcode:
        while True:
          ans_data = fans.readline().rstrip()
          code_data = fcode.readline().rstrip()

          if ans_data != code_data:
            print("\nTest case mismatch:", self.ifilelist[index])
            print("Your output    :", code_data)
            print("Expected output:", ans_data)
            return False

          # end of file
          if ans_data == "" and code_data == "":
            break

    # all correct for current test case
    return True


  # check for infinite loop in the code 
  def infinite_loop(self):
    # check for infinite loop
    whileTrue = 0
    with open(self.folder+"/"+self.codefile, "r") as f:
      while True:
        line = f.readline()
        if line == "":
          break

        line = line.rstrip().replace(" ", "")
        if "whileTrue:" in line:
          whileTrue += 1
        if "break" in line:
          whileTrue -= 1

    if whileTrue > 0:
      print("\nYour code may have an infinite loop")
      return True
    else:    
      return False


  # save codes from screen
  def save_codes(self):
    # read codes from input
    codes = []
    blankline = 0
    first_entry = True
    while True:
      line = input()

      # flush input buffer
      if first_entry:
        while line == "":
          line = input()
        first_entry = False
      
      # append code till double blanklines occur
      codes.append(line)
      if line == "":
        blankline += 1
        if blankline > 2:
            break         
      else:
        blankline = 0

    # save to code file
    with open(self.folder+"/"+self.codefile, "w") as f:
      for i in codes:
        f.write(i+"\n")

    print("- submitted -")


  # grade by:
  # 1. feeding each test case file to code
  # 2. generate output file
  # 3. compare with test case output file
  def grade(self):

    # loop for each test case
    all_correct = True
    count_correct = 0
    for i in range(len(self.ifilelist)):

      # if test case is specified, set index to the test case
      if self.ifile != "":
        i = self.ifilelist.index(self.ifile)

      # generate output file from code
      self.start_timer()
      print(("Checking "+self.ofilelist[i]).ljust(13+self.maxlen, " "), end="", flush=True)
      Thread(target=self.timer).start()
      command = 'python "' + self.folder + "/" + self.codefile + '" < "' + self.folder + "/" + self.ifilelist[i] + '" > "' + self.folder + "/" + self.codeout + '"'
      os.system(command)
      self.end_timer()

      # print time lapsed
      print("[time:", str(self.time_lapse()) + "]", end="", flush=True)

      # compare code output with test case output file
      if not self.match(i):
        all_correct = False
        print()
        #break
      else:
        print("......correct")
        count_correct += 1

      # break if running only specified testcase
      if self.ifile != "":
        break    

    # check if there is infinite loop
    # if not self.infinite_loop():
    #   # display result
    #   if all_correct:
    #     print("\nAll outputs matched")
    self.infinite_loop()
    print("\n" + str(count_correct),"out of", len(self.ifilelist),"correct")

    #cleanup
    with open(self.folder+"/"+self.codefile, "w") as f1:
      with open(self.folder+"/"+self.codeout, "w") as f2:
        f1.write("")
        f2.write("")


  def intro(self):
    print("\n\n=======================================================\n")
    print("Before running the grader:")
    print("1) A folder with all the testcases must be created for each question")
    print('2) All testcase input files must end with extension ".in"')
    print('3) All testcase ouput files must end with extension ".out"')
    print("4) Each testcase input file must have a corresponding output file\n   with the same name (eg. s1.1.in and s1.1.out)")
    print("5) input() command should be used with rstrip()")
    print("6) Codes should not have more than 2 consecutive blank lines")


  def main(self):

    # cleanup codefiles
    self.cleanup()

    # input folder name
    while True:
      self.folder = input("\nEnter folder name: ").upper()
      try:
        with open(self.folder+"/"+self.codefile, "w"):
          with open(self.folder+"/"+self.codeout, "w"):
            pass
        if self.read_file_lists():
          break
      except:
        print('Invalid folder name "' + self.folder + '"')

    # specify test case if any, else all test cases will be used
    while True:
      self.ifile = input("\nEnter testcase file [or hit enter to test all]: ")
      if self.ifile != "":
        if self.ifile in self.ifilelist:
          break
        else:
          print("Invalid entry")
      else:
        break

    # grade
    end = False
    while not end:      
      print("\nPaste codes below and hit enter:\n")
      self.save_codes()
      self.grade()
      while True:
        print("\n=======================================================")
        inp = input("\nRe-run test? [y/n] ").upper()
        if inp == 'Y':
          break
        elif inp == 'N':
          end = True
          break
        else:
          print("Invalid entry")
