#!/usr/bin/python
# @file: auto.py
# @author: Bread <breaddawson@gmail.com>
# @date: 08/07/11
# @brief: 

# this is for circuit testbench
# 1. no valid & no compress
# 3. only input vector can be xor
# 4. XOR & Random use the same solving methods with ATS08 (resolve())
# 5. ROW use partition, evalu, feedback, and re-stimulate
# 6. XOR & Random & ROW use the same evaluate(): partition, evaluate and get the average
# 7. XOR & Random & ROW use the same coverage(): cals how many stuck-at-0/1 errors can
#    be found, which means how many bits can be set as both 0 and 1.

import math
import random
import os
import sys
#from decimal import Decimal
import time

if (len(sys.argv) < 4):
    print "Usage: python rows.py testbench_file vector_num run_times"
    print len(sys.argv)
    sys.exit(-1)

ori_testbench = sys.argv[1]
n_vector = int(sys.argv[2])
run_times = int(sys.argv[3])

# print solution in integer or not
cf_int_solution = 0
# print solution in string or not
cf_str_solution = 0

def baseto(num,base=2,length=0):
    '''
    @description
      convert a number from dec to base(binary, octal or hex)
    @param
      num: the decimal number u want to convert
      base: the system u want to convert to
    @return:  a string
    '''
    result=[]
    reverse=""
    while True:
        num, rem = divmod(num,base)
        result.append(str(rem))
        if not num:
            break 
    reverse = ''.join([x for x in result[::-1]])
    for i in range(0,length-len(reverse)):
        reverse = "0" + reverse
    return reverse
    
# end of def baseto

# determin if target is in the array
#
# @param array: array
# @param target: target
# @param start: the start position
# @param length: how many elements need to be checked
# @return 1 if target is in the array, 0 if not
# 
def is_in(array, target, length, start=0):
    if length > len(array) - start:
        print "the param 'n' of is_in is too big!!!"
        sys.exit(-1)
    i = 0
    for i in range(start,start+length):
        if array[i]==target:
            return 1
    return 0

# open the testbench file and get the literal num and clause num
# n_literals = literal num,
# n_clauses = clause num,
# @param filename : the testbench file name
# @return a tuple [0]: num of literals [1]: num of clauses
def get_num(testbench_file):
    n_literals = 0
    n_clauses = 0
    f_tb = open(testbench_file)
    for line in f_tb:
        if line[0]=='p':
            break
    line = line.split()
    n_literals=int(line[2])
    n_clauses=int(line[3])
    f_tb.close()
    return (n_literals, n_clauses)
#end of def get_num

# @description: 
#    1) update n_litearl and n_clauses
#    2) delete the xor clauses
# @param testbench_file: the filename needed updated
# @param literal: the number of xor literals which will be added
# @param clause: the number of xor literals which will be added
# 
def update_num(testbench_file, literal, clause):
    literal = int(literal)
    clause = int(clause)
    f_tb = open(testbench_file,"r")
    content =""
    line =""
    record = True
    for line in f_tb:
        if line[0]=='p':
            line = line.split()
            n_literals = int (line[2]) + literal
            n_clauses = int (line[3]) + clause
            content += "p cnf " + str(n_literals) + " " + str(n_clauses) + "\n"
            continue
        elif line.count("c XOR BEGIN"):
            record = False
            continue
        elif line.count("c XOR END"):
            record = True
            continue
        if record and line != '\n':
            content += line
    f_tb.close()
    f_tb = open(testbench_file,"w+")
    f_tb.write(content)
    f_tb.close()
# end of def update_num

# check out the minisat logfile to see if it's sat,
# retrieve the result to var 'sat_result' if sat, and return 1
# @param sat_file: the file containing solution
# @param time_file: the file containing resolving time
# 
# @return: a tuple named result
#       result[0]: 1 if sat, 0 if unsat
#       result[1]: the solving time
#       result[2]: a string containg solution if sat
#
def check_sat(sat_file, time_file="None"):
    try:
        f_sat = open(sat_file)
    except IOError:
        print sat_file, "can not be opened, plz check it out"
        sys.exit(-1)
#    global sat_result
#    global solv_time
    succ = 0
    sat_result = "Failed"
    solv_time = 0.0
    line = ""
    while True:
        line = f_sat.readline()
        if len(line) == 0:
            break
        if line.count("UNSAT") > 0:
            break
        elif line.count("SAT") > 0:
            # get the result
            sat_result = f_sat.readline()
            succ = 1
            break
    f_sat.close()
    if time_file != "None":
        try:
            f_time = open(time_file)
        except IOError:
            print "f_time ",f_time, "can not be opened, plz check it out"
            sys.exit(-1)
        while True:
            line = f_time.readline()
            if len(line) == 0:
                break
            if line.count("CPU"):
                line = line.split()
                
#                print "*****", line[3]
                
                solv_time = float(line[3])
    return (succ, solv_time, sat_result)
# end of def check_sat

# generate different literals randomly
# @param power: the num of literal
def gen_literal(power):
    global xor_literal
    global input_literals
    if power > input_literals[0]:
        print "we can't get ", power , " different literals from only",\
         input_literals[0], "ones!"
        sys.exit(-1)
        
    run_times = 0
    thres = 20   
     
    while True:
        i = 0
        while i < power and run_times < power * thres:
#            print input_literals
            rand = random.randint(1,input_literals[0])
            real_rand= int(input_literals[rand])
            run_times += 1
            # if this literal has not been seleted
            if (not is_in(xor_literal, real_rand, i)):
                xor_literal[i]=real_rand
                i= i+1
        if run_times >= power * thres:
            print str(power*thres), " times have been tried"
            print "but still can not find enough random numbers"
            sys.exit(-1)
#         print xor_literal, " " , all_xor_literals
        temp_literal = xor_literal
        temp_literal.sort()
        if not is_in(all_xor_literals,temp_literal,n_vector):
            break
#     print "out gen_literal"
#         else:
#             print "random is "+ str(rand)
# end of gen_literal

def par_gen_clauses(testbench_file, n_xor_clauses, n_from, n_length):
    '''
    @description:
        generate n_xor_clauses xor clauses and write into testbench_file
        
           let n = n_xor_clauses 
        
        1) input_literals[0] * (2/3) < n
            exit because there're no enough literals
        2) n_from<0 (this is the 1st time)
            n_from = 1, n_length = input_literals[0]
            we choose literals from all the inputs
        3) n_length*(2/3) < n_xor_clauses
            n_length               => (2/3)*n_length
            (all_input - n_length) => n_xor_clauses - (2/3)*n_length
            
            and the latter < the former
    @param:
        testbench_file: the testbench file name
        n_xor_clauses: how many clauses we need
        n_from: the start index of least stimulated row
        n_length: the length of the least stimulated row 
    @return:
        nothing
    '''
    global all_xor_literals
    global xor_clauses
    
    # if n_xor_clauses > num of input literals 
    # we can not get enough xor literals
    
    if input_literals[0] * 2/3 < n_xor_clauses:
        print "we can't get", n_xor_clauses, "different literals from only",\
        input_literals[0], "ones!"
        sys.exit(-1)
            
    # if n_from < 0 or n_to < 0(1st time)
    # generate literals from all input literals
    if n_from<0 or n_length<0:
#        print "n_from,n_length", n_from, n_length
#        print "n_from(" + str(n_from) +") < 0 or n_length(" + str(n_length) + ") < 0,"\
#        " use all input literals instead"
        n_from = 1
        n_length = input_literals[0]
    
    # if the least stimulated row does not have enough literals
    # we get the left ones from other rows
    if n_xor_clauses > n_length*2/3:
        n_rows = n_length*2/3
    else:
        n_rows = n_xor_clauses 
    
    # improve partition
    if n_length != input_literals[0]:
        n_rows = 0
    
    n_left = n_xor_clauses - n_rows
    
    if n_left > (input_literals[0] - n_length)*2/3 :
        print n_length, "=>", n_rows, input_literals[0]-n_length, "=>", n_left
        print " n_xor_clauses is too large. we can not find an appropriate divide"
        sys.exit(-1)

    #  n_length => n_rows
    #  input_literals[0] - n_length => n_left
    
    
    # xor_literals contains all literals we generated
    # we use this ds in order not to get the same literals
    xor_literals = [0 for i in range(0,n_xor_clauses)]
    
    while True:
        
        # 1st step: n_length => n_rows
    
        #copy the literals in the least stimulated row
        temp_input = input_literals[n_from:n_from+n_length]
        n = n_length
        
        for i in range(0,n_rows):
            rand = random.randint(0,n-1)
            real_rand = int (temp_input[rand])
            temp_input[rand] = temp_input[n-1]
            n-=1
            xor_literals[i] = real_rand
        
        # 2nd step: (all_input - n_length) => n_left
        
        # copy the left input literals
        temp_input = input_literals[1:n_from]
        temp_input.extend(input_literals[n_length:])
        n = input_literals[0] - n_length
        
        for i in range(0,n_left):
            rand = random.randint(0,n-1)
            real_rand = temp_input[rand]
            temp_input[rand] = temp_input[n-1]
            n-=1
            xor_literals[n_rows+i] = real_rand
        
        
        # check to see if this row of literals are the same with previous rows
        # if not, append it to all_xor_literals 
        temp_literals = xor_literals[:]
        temp_literals.sort()
        if not is_in(all_xor_literals,temp_literals,len(all_xor_literals)):
            all_xor_literals.append(temp_literals)
            break        
        
    # now we get all the xor literals we need in xor_literals
            
    f_tb = open(testbench_file ,"a")
    f_tb.write("\nc XOR BEGIN\n")
    for i in range(0,n_xor_clauses/2):
        x = int(xor_literals[2*i])
        y = int(xor_literals[2*i+1])
        xor_clauses[2*i] = str(x) + " " + str(y) + " 0"
        xor_clauses[2*i+1] = str(-x) + " " + str(-y) + " 0"
        f_tb.write(xor_clauses[2*i] + "\n")
        f_tb.write(xor_clauses[2*i+1] + "\n")
    
    if n_length != input_literals[0]:
        dec_ran = random.randint(0,2**n_length-1)
        bin_ran = baseto(dec_ran, 2, n_length)
        for j in range(0,n_length):
            if bin_ran[j] == '0':
                f_tb.write("-")
            f_tb.write(input_literals[n_from+j] + " 0\n")
    f_tb.write("c XOR END\n")
    f_tb.close()
#end def par_gen_clauses

            
def gen_xor_clauses(power):
    global xor_clauses
    # general 2 * $power different literals randomly
    # which will be stored in xor_literal
    gen_literal(2 * power) 
    # output the xor literals
    # for i in range (0,2*power):
    #     print xor_literal[i]

    # generate the xor clauses every 2 literals
    # there're 2 * power literals stored in xor_literal
    # we need power xor clauses, so every time we retrieve two literals x, y
    # 1 <-> x XOR y = ( x + y) * (-x + -y)
    # 
    
    for i in range (0,power):
        x = xor_literal[2*i]
        y = xor_literal[2*i+1]
        xor_clauses[2*i] = str(x) + " " + str(y) + " 0"
        xor_clauses[2*i+1] = str(-x) + " " + str(-y) + " 0"

# end of def gen_clause


# write the xor clauses into testbench file
def add_xor_clause(testbench_file):
    i = 0
    f_tb = open(testbench_file ,"a")
    f_tb.write("\nc XOR BEGIN\n")
    for i in range(0,n_xor_clauses):
        f_tb.write(xor_clauses[i] + "\n")
    f_tb.write("c XOR END\n")
    f_tb.close()
#end def add_xor_clause


# @description
#   1) read all the solutions in the filename given
#   2) calculate to see if they're uniform sampled
#   3) return a float
# @param filename: the sat result file u want to evaluate
# @return: a float num from 0 to 1, the less, the better
def evaluate(filename):
    '''
    @description
    this is the evaluation function for xor_par_rand
    
    1) read all the solutions in the filename given
       and then split them into rows ( log2k bits one row)
    2) calculate to see if they're uniform sampled
    3) find the least stimulated row (has largest evaluation)
    @param
        filename: the file which contains the results
    @return
        a float num from 0 to 1, the less, the better
    '''
    
    # here's the global vars which will be used in this function
    # global input_literals
    
    
    try:
        f = open(filename)
    except IOError:
        print filename, " does not exists, plz check it out"
        sys.exit(-1)
        
    line = f.readline()
    line = line.split()
    # get the number of solutions
    # because the solution file wrote:
    # n_read / n_need Got, .....
    n_real = int(line[0])
    n_need = int(line[2])
    
#    print "n_real=", n_real, " n_need=", n_need
    
    # actually this detection is redundant, since if we can not 
    # get enough solutions, the program will exit when resolving
#    if n_real < n_need:
#        print "n_real < n_need!!"
#        exit(-1)
        
    # only the input vectors will be evaluated
    
    # row_size is upper[log2(n_real)]
    row_size = float(math.log(n_real,2))
    if row_size > int(row_size):
        row_size = int(row_size) + 1
    else:
        row_size = int(row_size)
    
    # how many rows the solution need to be splited into
    # it's lower_bound(input number)/row_size
    n_rows = input_literals[0]/row_size
    # solution[n_rows][n_real]
    solution = [["" for x in range(0,n_real)] for i in range(0,n_rows)]    

    i = 0
    while True:
        line = f.readline()
        if (len(line)==0):
            break
        elif line.count("Solution") > 0:
            #read the solution
            ori_solution = f.readline()
            #split the solution into singel elements
            split = ori_solution.split()
            
            # print the solution in str, such as
            # -1 2 3 -4 ...
            if cf_str_solution:
                for j in range(0,len(split)):
                    print split[j],
                print            

            #put the solution element into each row
            #convert the solution to Binary String
            #for example, "-1, 2, 3, -4" to "0110"
            
            # i_input is index of the literal in input_literals
            i_input = 0
            for j in range(0,len(split)):
                # filter non-input literals out
                if not is_in(input_literals, str(abs(int(split[j]))), input_literals[0], 1):
                    continue
                # get the row index
                row_num = i_input/row_size
                i_input += 1
                # if j/power > n_rows-1, which indicates that there're some literals
                # left too few for a row, so we merge them into the last row
                if row_num > n_rows-1:
                    row_num = n_rows-1

                if int(split[j]) < 0:
                    solution[row_num][i] += "0"
                else:
                    solution[row_num][i] += "1"
            i = i + 1
    
    # if there're not enough solutions, exit
    if i != n_real:
        print "solution num < n_real !!"
        exit(-1)
        
    #enf of while
    f.close()
    
    eval = [0.0 for x in range(0,n_rows)]
    eval_ave = 0.0
    
#    print "input_literals:", input_literals, "row_size:", row_size, "n_rows:", n_rows
    # output all the solutions in rows
#    for aa in range(0,n_real):
#        for bb in range(0,n_rows):
#            print solution[bb][aa],
#        print
    # convert the solution to int and then sort in rows
    # that is, first convert solution[0][0~n_real-1], sort the n_real ones, evaluate
    # then solution[1][1~n_real-1]
    # ...,finally solution[n_rows-1][0~n_real-1]
    for j in range(0, n_rows):
        for k in range(0,n_real):
            solution [j][k] = int(solution[j][k],2)
        solution[j].sort()
        
        row_len = row_size
        # the last row may have more than row_size elements
        if j == n_rows-1:
            row_len = input_literals[0] - row_size * j
    
    # n = row_len
    # calculate a = s0 + 2^n - s(n_real-1)
    # calculate b = Sigma (i= 1 ~ n_real)| (2^n)/k - (s(i) - s(i-1) ) |
    # calculate c = (a+b) / (2^n)
    # if n_need = k, then max c = 2 ** bitwidth  * (k-1)/k
        total = 2 ** row_len
        max = 1.0 * 2 * total * (n_real-1)/n_real
        average = float(total)/n_real

        sum = abs(solution[j][0] + total - solution[j][n_real-1] - average)

        for i in range(1,n_real):
            sum += abs(solution[j][i] - solution[j][i-1] - average)

        eval[j] = float(sum)/max
        eval_ave += eval[j]

    #print the integer
    if cf_int_solution:
        for i in range(0,n_real):
            for j in range(0,n_rows):
                print solution[j][i],
            print
    
    return eval_ave/n_rows

# end of def evaluate





def row_evaluate(filename):
    '''
    @description
    this is the evaluation function for xor_par_rand
    
    1) read all the solutions in the filename given
       and then split them into rows ( log2k bits one row)
    2) calculate to see if they're uniform sampled
    3) find the least stimulated row (has largest evaluation)
    @param
        filename: the file which contains the results
    @return
        n_from: the index of the first element in least stimulated row
        n_length: the size of the least stimulated row
    '''
    
    # here's the global vars which will be used in this function
    # global input_literals
    
    
    try:
        f = open(filename)
    except IOError:
        print filename, " does not exists, plz check it out"
        sys.exit(-1)
        
    line = f.readline()
    line = line.split()
    # get the number of solutions
    # because the solution file wrote:
    # n_read / n_need Got, .....
    n_real = int(line[0])
    n_need = int(line[2])
    
#    print "n_real=", n_real, " n_need=", n_need
    
    # actually this detection is redundant, since if we can not 
    # get enough solutions, the program will exit when resolving
#    if n_real < n_need:
#        print "n_real < n_need!!"
#        exit(-1)
        
    # only the input vectors will be evaluated
    
    # row_size is upper[log2(n_real)]
    row_size = float(math.log(n_real,2))
    if row_size > int(row_size):
        row_size = int(row_size) + 1
    else:
        row_size = int(row_size)
    
    # how many rows the solution need to be splited into
    # it's lower_bound(input number)/row_size
    n_rows = input_literals[0]/row_size
    # solution[n_rows][n_real]
    solution = [["" for x in range(0,n_real)] for i in range(0,n_rows)]    

    i = 0
    while True:
        line = f.readline()
        if (len(line)==0):
            break
        elif line.count("Solution") > 0:
            #read the solution
            ori_solution = f.readline()
            #split the solution into singel elements
            split = ori_solution.split()
            
            # print the solution in str, such as
            # -1 2 3 -4 ...
            if cf_str_solution:
                for j in range(0,len(split)):
                    print split[j],
                print            

            #put the solution element into each row
            #convert the solution to Binary String
            #for example, "-1, 2, 3, -4" to "0110"
            
            # i_input is index of the literal in input_literals
            i_input = 0
            for j in range(0,len(split)):
                # filter non-input literals out
                if not is_in(input_literals, str(abs(int(split[j]))), input_literals[0], 1):
                    continue
                # get the row index
                row_num = i_input/row_size
                i_input += 1
                # if j/power > n_rows-1, which indicates that there're some literals
                # left too few for a row, so we merge them into the last row
                if row_num > n_rows-1:
                    row_num = n_rows-1

                if int(split[j]) < 0:
                    solution[row_num][i] += "0"
                else:
                    solution[row_num][i] += "1"
            i = i + 1
    
    # if there're not enough solutions, exit
    if i != n_real:
        print "solution num < n_real !!"
        exit(-1)
        
    #enf of while
    f.close()
    
    eval = [0.0 for x in range(0,n_rows)]
    eval_ave = 0.0
    
#    print "input_literals:", input_literals, "row_size:", row_size, "n_rows:", n_rows
    # output all the solutions in rows
#    for aa in range(0,n_real):
#        for bb in range(0,n_rows):
#            print solution[bb][aa],
#        print
    # convert the solution to int and then sort in rows
    # that is, first convert solution[0][0~n_real-1], sort the n_real ones, evaluate
    # then solution[1][1~n_real-1]
    # ...,finally solution[n_rows-1][0~n_real-1]
    for j in range(0, n_rows):
        for k in range(0,n_real):
            solution [j][k] = int(solution[j][k],2)
        solution[j].sort()
        
        row_len = row_size
        # the last row may have more than row_size elements
        if j == n_rows-1:
            row_len = input_literals[0] - row_size * j
    
    # n = row_len
    # calculate a = s0 + 2^n - s(n_real-1)
    # calculate b = Sigma (i= 1 ~ n_real)| (2^n)/k - (s(i) - s(i-1) ) |
    # calculate c = (a+b) / (2^n)
    # if n_need = k, then max c = 2 ** bitwidth  * (k-1)/k
        total = 2 ** row_len
        max = 1.0 * 2 * total * (n_real-1)/n_real
        average = float(total)/n_real

        sum = abs(solution[j][0] + total - solution[j][n_real-1] - average)

        for i in range(1,n_real):
            sum += abs(solution[j][i] - solution[j][i-1] - average)

        eval[j] = float(sum)/max
        eval_ave += eval[j]

    #print the integer
    if cf_int_solution:
        for i in range(0,n_real):
            for j in range(0,n_rows):
                print solution[j][i],
            print
    

    max = max_pos = -1
    for i in range(0,n_rows):
        if eval[i] > max:
            max = eval[i]
            max_pos = i
            
        
    # max_pos is the index of least simulated row

    # add 1 here because literals named from 1
    # we need to random from input_literals[n_from~n_from+n_length-1]
    n_from = max_pos * row_size + 1
#    print "######", input_literals, n_from, row_size
    n_length = row_size
    if max_pos == n_rows-1:
        n_length = input_literals[0] - max_pos * row_size
    
    return [n_from,n_length, eval_ave/n_rows]
# end of def row_evaluate


def resolve(ori_bench_file, result_file, xor=0):
#    global n_vector # how many vectors we want
#    global resolv_thres # threshold times we'll try to resolve
    
    #change time
    global_time1 = time.time()
    
    
    # the temp testbench file name we'll use in this function
    testbench_file = "testbench.cnf" 
    n_tried = 0 #how many times we have tried
    n_re_vector = 0 # how many vectors we got
    solv_time = 0.0 # how long before we got n_vector vectors   
    
    global all_xor_literals
    all_xor_literals =[[0 for x in range(0,2 * power)] for y in range(0,n_vector)]
           
    
    # ruin the result_file
    f_tb = open(result_file,"w+")
    f_tb.write("                                                                                             \n\n");
    f_tb.close()
    
    
    # ori_testbench is given in argv
    # copy the original file in order not to ruin it
    os.system("cp " + ori_testbench + " " + testbench_file)        
    
    # update the clauses num if xor is specified
    if xor:
        update_num(testbench_file, 0, n_xor_clauses)

    # if n_re_vector < n_vector , which indicates we haven't got enough test vectors
    # then we need to go on resolving
    # but if we tried too many times ( the threshold is resolv_thres * n_vector)
    # and still can't get as many as we want
    # we'll give up
    while (n_tried < resolv_thres * n_vector) and (n_re_vector < n_vector):
        sat_result = ""
        sat = (0,0,0)

        
        while (n_tried < resolv_thres * n_vector) and (not sat[0]):
            if xor :
                update_num(testbench_file,0,0) # delete the xor clauses added last time
                gen_xor_clauses(power) #generate new xor clauses
            #         print xor_literal
            #         print "xor_clauses:\n ", xor_clauses
            #         for i in range(0,power):
            #             all_xor_literals [n_re_vector][i] = xor_literal[i]
                xor_literal.sort()
                all_xor_literals [n_re_vector] = xor_literal[:]
                #         print "all", all_xor_literals[n_re_vector]
                #         print "****",xor_clauses, "****"
                add_xor_clause(testbench_file) # add them to testbench file
                # we needn't to update n_literal or n_clause
                # that's because n_xor_literal & n_xor_clause is fixed as soon as the vector num is specified
                # so we just need to add n_xor_literal and n_xor_clauses once
            os.system("./minisat " + testbench_file + " " + sat_file + " > " + time_file)
            n_tried = n_tried + 1
            

            sat = check_sat(sat_file, time_file)
            solv_time += sat[1]

            
        if (n_tried >= resolv_thres * n_vector):
            print n_vector,"Vectors Needed, ", n_tried, "Times Tried"
            break

        
        # every time we get a new solution
        # we need to add it to the testbench file
        # and of course we need to update n_literal and n_clause ( +1 every time )
        n_re_vector = n_re_vector + 1
    #    print "*****", sat , "*******"
        sat_result = sat[2]
    #    print "sat_result:"
        sat_result = sat_result.split()


        # 1) add clause number by 1 
        # 2) delete XOR clauses
        update_num(testbench_file, 0, 1)
        
        # in respect to the performance, we write the confilt clause directly into file
        # instead of write after generate the clause first
        f_tb = open(testbench_file, "a")
        for i in range(0,ori_n_literal):
            f_tb.write(str(-int(sat_result[i])) + " ")
        f_tb.write("0\n")
        f_tb.close()
        

        #output the xor clauses and solution to solution.txt
        try:
            f_tb = open(result_file,"a")    
        except IOError:
            print "resolve(): ", result_file, " can't be opened, plz check it out"
            sys.exit(-1)
        f_tb.write("********" + str(n_re_vector) + "********\n" )
        
        # if xor is specified, output the xor clauses into result_file
        if xor:
            f_tb.write("XOR Clauses:\n")
            for i in range(0,n_xor_clauses):
                f_tb.write(xor_clauses[i] + ", ")

        
        #output the solution into result_file
        f_tb.write("\nSolution: \n" )   
        for i in range(0,ori_n_literal):
    #        print j, "**", sat_result[j], "**"
            f_tb.write(sat_result[i] + " ")
        f_tb.write("\nSolving Time: " + str(sat[1]) + "\n")
        f_tb.write("\n")    


    # if n_re_vector is less than n_vector
    # we need to generate the left by enumerating the solutions already generated
    # but actually we need not really do this
    # we can do this when evaluating it
    if n_re_vector < n_vector:
        print "the solutions of this benchmark is less than " + str(n_vector) + " !!!"
        sys.exit(-1)
    f_tb = open(result_file,"r+")
    f_tb.write(str(n_re_vector) + " / " + str(n_vector) + " Vectors Got, " \
        +  str(n_tried) + " Times Tried, Using " + str(solv_time) + "s" )
    f_tb.close()
    
#    if xor:
#        print "XOR",
#    else:
#        print "RANDOM",
#    print " Solving Done, " + str(n_re_vector) + "/" + str(n_vector) + "generated"
#    print "Solving time: " + str(solv_time)
#    return (n_re_vector, solv_time)
    return (n_re_vector, time.time()-global_time1)
#def resolve

def xor_par_rand(ori_bench_file, result_file):
    '''
    @description: get the resolutions even distributed by
      1) adding xor clauses
      2) get all the k solutions gradually:
        k/3, k/3+k/6, k/3+k/6+k/12, k/3+k/6+k/12+k/24.. k
      3) evaluate the solutions in rows every time we resolve,
         find the ones not enough simulated and add xor clauses in respect to them
         then resolve again. 
         Repeat in this way until we get k solutions
    @parameters:
        ori_bench_file: the original testbench file
        result_file: we will output the solutions here
    @return 
        n_re_vector: how many soltions we get
        solv_time: how long it takes to solve these solutions
    '''
    global_time2 = time.time()
    
    # set these two vars as global because:
    # 1. all_xor_literals will be use in par_gen_clauses(), and in this function it 
    #   be cleared every time we start to solve a new row of solutions
    # 2. xor_clauses will be filled with xor clauses which are need in one pass 
    #   of solving in par_gen_clauses()
    #   and we need to write them into solution file in this function
    global all_xor_literals
    global xor_clauses
    
    testbench_file = "testbench.cnf" # the temp testbench file
    n_tried = 0 #how many times we have tried
    n_re_vector = 0 # how many vectors we got
    solv_time = 0.0 # how long before we got n_vector vectors       
    
    # ruin the result_file
    f_tb = open(result_file,"w+")
    # write blank into result_file in order to insert statistic infos in the end
    f_tb.write("                                                                \
                                 \n")
                                
    f_tb.write("Input: " + str(input_literals[0]) + "\n")
    for i in range(1, input_literals[0]+1):
        f_tb.write(input_literals[i] + ", ")
    f_tb.write("\n\n")
    f_tb.close()
    
    # we need to get all the solutions gradually,just like this
    # k/3, k/3+k/6, k/3+k/6+k/12, k/3+k/6+...+k/(3*2^m), k
    # when k/(3*2^m)<10, next time we need not get k/(6*2^m) solutions
    # but get (k- what_we_had_now) solutions instead.
    # so here's some vars help us to do this:
    
    divide = 3 # first 3, then *=2 each time
    # n_sol_part is delta nums we solve each time
    # n_vector is a global var which indicates the number of all vectors
    n_sol_part = n_vector/divide
    least_row = -1 # the least sitmulated row, initialized as -1
    
    # ori_testbench is given in argv
    # copy the original file in order not to ruin it
    os.system("cp " + ori_testbench + " " + testbench_file)     
    
    last_n_xor_clauses = 0
    
    # the outest loop
    # we need n_vector solutions
    # n_re_vector is the total number of solutions now
    # i_row is the row index (1,2,3,...)
    i_row = 0
    n_from = n_length = -1; 
    while (n_tried < resolv_thres * n_vector) and (n_re_vector < n_vector):
        
        # 1) add log(n_sol_part) xor clauses into testbench
        #    the xor literals get from the least row, if there're not
        #    enough ones or in first run, get the left literals randomly
        #    from the ones which r not in the least stimulated row
        # 2) get n_sol_part solutions
        # 3) evaluate every row and find the row least stimulated
        # 4) n_sol_part /= 2 
        
        i_row += 1
        # if n_sol_part is less than 10, we need not to get n_sol_part/2 solutions
        # next time, we get all the left solutions directly
        if n_sol_part < n_vector/16:
            n_sol_part = n_vector - n_re_vector
# row debug
#        print "***", str(i_row)+"st row,", n_sol_part, \
#            "("+ str(n_re_vector+1) +"~" + str(n_re_vector+n_sol_part) + ") solutions needed"
#
#        print "n_from,n_length:", n_from, n_length
        # we need upper_bound(log2(n_sol_part)) xor clauses
        # and 2 literals each clause, such as 1<-> x XOR y
        # n_xor_literals = 2 * upper_bound(log2(n_sol_part))
        n_xor_literals = float(math.log(n_sol_part,2))
        if n_xor_literals > int(n_xor_literals):
            n_xor_literals = int(n_xor_literals + 1)
        else:
            n_xor_literals = int(n_xor_literals)
        n_xor_literals *= 2
        
        # we need n_xor_literals/2 xor clauses
        # but 1<-> x XOR y = (x+y) * (-x + -y)
        # so actually we still need n_xor_literals xor clauses
        n_xor_clauses = n_xor_literals
        
        # all_xor_literals contains all the xor literals we generated in this row
        # we keep this array in order not to get the same literals
        
        all_xor_literals = []
        
        # update the clauses num because we need to add xor clauses into testbench
        update_num(testbench_file, 0, -last_n_xor_clauses)
        update_num(testbench_file, 0, n_xor_clauses)
        last_n_xor_clauses = n_xor_clauses
        
        # this is the second loop
        # we get n_sol_part solutions every row
        n_sol_now = 0
        
        while (n_tried < resolv_thres * n_vector) and (n_sol_now < n_sol_part):
            sat_result = ""
            sat = (0,0,0)
            
            while (n_tried < resolv_thres * n_vector) and (not sat[0]):
                
                update_num(testbench_file,0,0) # delete the xor clauses added last time
                
                xor_clauses = ["" for x in range(0,n_xor_clauses)]
                # 1. generated n_xor_clauses xor clauses using the literals
                # from input_literals[n_from] to input_literals[n_from + n_length+1]
                # 2. write them into testbench files
                par_gen_clauses(testbench_file, n_xor_clauses, n_from, n_length)
                
                # we needn't to update n_literals or n_clauses
                # that's because n_xor_clauses is the same every time we solve
                # so we just need to add n_xor_literals and n_xor_clauses once
                os.system("./minisat " + testbench_file + " " + sat_file + " > " + time_file)
                n_tried = n_tried + 1

                sat = check_sat(sat_file, time_file)
                solv_time += sat[1]
                
            if (not sat[0]):
                print n_vector,"Vectors Needed, ", n_tried, "Times Tried"
                sys.exit(-1)
            
            # every time we get a new solution
            # we need to add it to the testbench file
            # and of course we need to update n_literal and n_clause ( +1 every time )
            n_re_vector += 1
            n_sol_now += 1
        #    print "*****", sat , "*******"
            sat_result = sat[2]
        #    print "sat_result:"
            sat_result = sat_result.split()

            # 1) add clause number by 1 
            # 2) delete XOR clauses
            update_num(testbench_file, 0, 1)
            
            # add conflict clause
            f_tb = open(testbench_file, "a")
            for i in range(0,ori_n_literal):
                f_tb.write(str(-int(sat_result[i])) + " ")
            f_tb.write("0\n")
            f_tb.close()

            #output the xor clauses and solution to result_file
            try:
                f_tb = open(result_file,"a")    
            except IOError:
                print "resolve(): ", result_file, " can't be opened, plz check it out"
                sys.exit(-1)
                
            # *** 3 (1 of 3th row) ***
            f_tb.write("********" + str(n_re_vector) + " (" + str(n_sol_now) +\
            "/" + str(n_sol_part) +" of " + str(i_row) + "th row) ********\n" )
            # output the xor clauses into result_file
            f_tb.write("XOR Clauses (" + str(n_xor_clauses) + "): \n From: ")
            f_tb.write("(" + str(n_from) + "," + str(n_length) + ")")
            # if n_from < 0, which indicates it's the first time
            # we select xor literals from all input literals
            if n_from < 0:
                f_tb.write("All input literals")
            else:
                # if the least stimuluated row doesn't have enought literals
                # to generated n_xor_clauses literals, the left ones will be 
                # generated from other input literals
                if n_xor_clauses > n_length*2/3:
                    f_tb.write( "\n  " + str(n_length*2/3)+": (" + str(n_length) +")")
                else:
                    f_tb.write( "\n " + str(n_xor_clauses) + ": (" + str(n_length) + ")" )
                for i in range(n_from,n_from+n_length):
                    f_tb.write(input_literals[i]+", ")
                if n_xor_clauses > n_length*2/3:
                    f_tb.write( "\n  " + str(n_xor_clauses-n_length*2/3)+ \
                        ": Other input literals")
            f_tb.write("\n Gen: ")
            for i in range(0,n_xor_clauses):
                f_tb.write(xor_clauses[i] + ", ")

            #output the solution into result_file
            f_tb.write("\nSolution: \n" )   
            for i in range(0,ori_n_literal):
        #        print j, "**", sat_result[j], "**"
                f_tb.write(sat_result[i] + " ")
            f_tb.write("\nSolving Time: " + str(sat[1]) + "\n")
            f_tb.write("\n")
            f_tb.close()
        
        # if we can not get enough solutions in this row, exit
        if n_sol_now < n_sol_part:
                print "the solutions of this benchmark is less than " + n_vector + " !!!"
                sys.exit(-1)
        
        # wrote statistic infos into result file
        # because of mass blanks written before, the stat infos won't ruin the
        # content of result file
        f_tb = open(result_file,"r+")
        f_tb.write(str(n_re_vector) + " / " + str(n_vector) + " Vectors Got, " \
            +  str(n_tried) + " Times Tried, Using " + str(solv_time) + "s" )
        f_tb.close()
#row debug
#        print " Solving Done, " + str(n_sol_now) + "/" + str(n_sol_part) + "generated"
        
        n_sol_part = n_sol_part * 2 / 3
        # the second loop is over
        # end of one partition(row) solving
        
        # evaluate all the solutions got, and get the least stimulated row
        # return n_from, n_length
        temp_evalu = row_evaluate(result_file)
        n_from = temp_evalu[0]
        n_length = temp_evalu[1]
#        print "***eval", temp_evalu[2]
#        print "n_from,n_length:", n_from, n_length
        
        
    # if n_re_vector is less than n_vector
    # we need to generate the left by enumerating the solutions already generated
    # but actually we need not really do this
    # we can do this when evaluating it
    
#    print " Solving Done, " + str(n_re_vector) + "/" + str(n_vector) + "generated"
#    print "Solving time: " + str(solv_time)
#    return (n_re_vector, solv_time)
    return (n_re_vector, time.time()-global_time2)
    
#end def xor_par_rand


def coverage(filename):
    ''' 
    @description
    check each literal to see if both 0 and 1 can be got
    @parameter
    filename: the result file we need for computing coverage
    @return a number which indicates how many literals can be coveraged
    @mechanism:
        we need an array cov[0~n_literals] to statistic this
        all the literals but input_literals will be checked
        cov[0]: the coveraged literal number
        cov[1~n_literals]:
        -1: the initial value
        0: 0 is coveraged
        1: 1 is coveraged
        2: both 0 and 1 is coveraged
        
        and the transitions are:
        
        if 0 is coveraged: -1->0 0->0 1->2 
        if 1 is coveraged: -1->1 1->1 0->2
    '''
    
    cov = [-1 for i in range(0,n_literals+1)]
    cov[0] = 0
    
    try:
        f = open(filename)
    except IOError:
        print filename, " does not exists, plz check it out"
        sys.exit(-1)
    
    # check all the solutions
    while True:
        line = f.readline()
        if (len(line)==0):
            break
        elif line.count("Solution") > 0:
            #read the solution
            solution = f.readline()
            
            #split the solution into singel elements
            split = solution.split()
            for j in range(0,len(split)):
                i = int(split[j])
                # if this literal is input literal, ommit it
                if is_in(input_literals,str(abs(i)),input_literals[0],1):
                    continue
                # if i=0 is coveraged
                # -1->0, 0->0, 1->2
                if i<0 and (cov[-i] == -1 or cov[-i]==1):
                    cov[-i] += 1
                # if i=1 is coveraged
                # -1->1, 0->2, 1->1
                elif i>0 and (cov[i]==-1 or cov[i]==0):
                    cov[i] += 2
    
    #check cov[1~n_literals] to see if there's 2
    for i in range(1,n_literals+1):
        if cov[i]==2:
            cov[0]+=1
    return cov[0]
#end coverage


# power is the number of xor clauses ( log(n) + 1)
power = int(math.log(n_vector,2))

if math.log(n_vector,2) != power:
    power+=1


# the solution file name
# using xor or not
xor_file = "xor.solution"
random_file = "random.solution"
for i in range(1, run_times+1):
    os.system("rm -rf xor.solution_" + str(i))
    os.system("rm -rf random.solution_" + str(i))
#    os.system("touch xor.solution_" + str(i))
#    os.system("touch random.solution_" + str(i))

time1 = time.time()

# the sat result file name
sat_file = "sat_file"
# the file containing the direct output of minisat
time_file = "time_file"

#get n_literals and n_clauses
num_tuple = get_num(ori_testbench)
n_literals = num_tuple[0]
n_clauses = num_tuple[1]

#backup the original literal number
ori_n_literal = n_literals

#get the input literals and stored them in input_literal
f_tb = open(ori_testbench)
while True:
    line = f_tb.readline()
    if len(line) == 0:
        break
    if line.count("c inputs") > 0:
        break

line = line.split()
input_literals = [0]
for i in range(2, len(line)):
    input_literals.append(line[i])
    input_literals[0] +=1

if input_literals[0] != len(line) - 2:
    print "input literals number is incorrect! plz have a check"
    sys.exit(-1)
    
#print input_literals


# valid[i] indicates if i need to be evaluated
# valid[0] indicates how many literals are valid
# valid = [1] * (n_literals+1)
# valid[0] = n_literals
# check if valid
#prune()
#print "valid =" , valid

# need to compress before evaluating
#compress_bit = 4
#os.system("cp " + ori_testbench + " compress_file")
#time1 = time.time()

#rectify = compress("compress_file", compress_bit)
#print "rectify =", rectify, "\n"

# the xor literals
xor_literal = [0 for x in range(0,2 * power)]
all_xor_literals =[[0 for x in range(0,2 * power)] for y in range(0,n_vector)]
                     
n_xor_clauses = 2*power
xor_clauses = [ "" for x in range(0,n_xor_clauses)]

# if we tired more than resolv_thres * n_vector times
# but still can not get n_vector vectors
# then we give up
resolv_thres = 10

#
#
#xor_par_rand(ori_testbench, row_file)
#
#print coverage(row_file), ori_n_literal

eval_xor = 0.0
eval_random = 0.0
eval_row = 0.0

time_xor = 0.0
time_random = 0.0
time_row = 0.0

cov_xor = cov_random = cov_row = 0

for i in range (0,run_times):
    
    xor_literal = [0 for x in range(0,2 * power)]
    all_xor_literals =[[0 for x in range(0,2 * power)] for y in range(0,n_vector)]
    xor_clauses = [ "" for x in range(0,n_xor_clauses)]    
    
    print "\n************** " , i+1, "**************"
    xor_file = "xor.solution_" + str(i+1)
    random_file = "random.solution_" + str(i+1)
    row_file = "row.solution_" + str(i+1)
    
    time1 = time.time()
    xor_result = resolve(ori_testbench, xor_file, 1)    
#    print "***time: resolve_xor_", i, " : ", time.time()-time1
#    time1 = time.time()
    random_result = resolve(ori_testbench, random_file, 0)
#    print "***time: resolve_random_", i, " : ", time.time()-time1
#    time1 = time.time()
    row_result = xor_par_rand(ori_testbench, row_file)
    
    time_xor += xor_result[1]
    time_random += random_result[1]
    time_row += row_result[1]
    
    print "\nXOR: ", xor_result[0] , "/", n_vector, " ", xor_result[1]
    temp_xor = evaluate(xor_file)
    print "eval: ", temp_xor
    eval_xor += temp_xor
    temp_cov = coverage(xor_file)
    cov_xor += temp_cov
    print "cov: ", temp_cov
    
    print "\nRANDOM:", random_result[0] , "/", n_vector, " ", random_result[1]
    temp_random = evaluate(random_file)
    print "eval: ", temp_random
    eval_random += temp_random
    temp_cov = coverage(random_file)
    cov_random += temp_cov
    print "cov: ", temp_cov
            
    print "\nROW:", row_result[0] , "/", n_vector, " ", row_result[1]
    temp_row = evaluate(row_file)
    print "eval: ", temp_row
    eval_row += temp_row
    temp_cov = coverage(row_file)
    cov_row += temp_cov    
    print "cov: ", temp_cov
            
    print "*******************************"

print "#### K =", n_vector, "### Runtimes =", run_times, "####"

print "XOR EVAL ", "%.3f" % (eval_xor/run_times), " TIME: ", "%.3f" % (time_xor/run_times), \
"COV:", str(cov_xor/run_times)+"/"+str(ori_n_literal-input_literals[0]), \
"%.3f" % (float(cov_xor)/run_times/(ori_n_literal-input_literals[0]))
print "RAN EVAL ", "%.3f" % (eval_random/run_times), " TIME: ", "%.3f" % (time_random/run_times), \
"COV:", str(cov_random/run_times)+"/"+str(ori_n_literal-input_literals[0]), \
"%.3f" % (float(cov_random)/run_times/(ori_n_literal-input_literals[0]))
print "ROW EVAL ", "%.3f" % (eval_row/run_times), " TIME: ", "%.3f" % (time_row/run_times), \
"COV:", str(cov_row/run_times)+"/"+str(ori_n_literal-input_literals[0]), \
"%.3f" % (float(cov_row)/run_times/(ori_n_literal-input_literals[0]))

print "===========================================\n\n\n\n"