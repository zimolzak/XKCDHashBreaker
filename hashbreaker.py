from multiprocessing import *
import string
import random

try:
     from skein import skein1024
except ImportError:
     print('Error: this program requires the PySkein module in order to run.')
     exit(1)


target = bin(int('5b4da95f5fa08280fc9879df44f418c8f9f12ba424b7757de02bbdfbae0d4c4fdf9317c80cc5fe04c6429073466cf29706b8c25999ddd2f6540d4475cc977b87f4757be023f19b8f4035d7722886b78869826de916a79cf9c94cc79cd4347d24b567aa3e2390a573a373a48a5e676640c79cc70197e1c5e7f902fb53ca1858b6', 16))[2:] + '0'

def main():
    import sys
    if sys.version_info[0] != 3:
        print('Error: This program requires Python 3.')        
        exit(1)
    cpuCores = cpu_count()
    threadPool = Pool(processes=cpuCores)
    for x in range(cpuCores):
        threadPool.apply_async(hash_brute_force, [x])
    while(True): pass

def hash_brute_force(idnum):
    num_correct_bits = 0
    attempt = 0
    while(True):
        if attempt % 5000 == 0:
            print('Core {}: attempt {}'.format(idnum, attempt))
        rand_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(256))
        digest = digest_str(rand_str)
        bin_string = bin(int(digest, 16))[2:].ljust(1024, '0')
        diff_bits = compare(bin_string)
        if diff_bits > num_correct_bits:
            print('INPUT STRING: {} - CORRECT BITS: {}'.format(rand_str, diff_bits))
            num_correct_bits = diff_bits
	    
            write_to_file(idnum, rand_str + ' ' + str(diff_bits))
        attempt += 1

def simulated_annealing(idnum):
     best_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(256))
     best_value = compare(digest_str(start_string), target)
     generation = 0
     while(True):
          if generation % 5000 == 0:
               print('Generation {}, best value: {}'.format(generation, best_value))
          successors = sa_gen_successors(best_string)
          best_loc_str = max(successors, key=lambda x: compare(digest_str(x)))
          best_loc_val = compare(digest_str(best_loc_str))
          if best_loc_val > best_value:
               best_value = best_loc_val
               best_string = best_loc_str
               write_to_file(idnum, best_loc_str + ' ' + best_loc_val)
          else:
               transition_prob = float(best_loc_val)/float(best_value)
               if random.random <= transition_prob:
                    best_value = best_loc_val
                    best_string = best_loc_str
                    write_to_file(idnum, best_loc_str + ' ' + best_loc_val)


def sa_gen_successors(string_in):
     neighbor_strings = []
     for x in range(100):
          neighbor_strings.append(''.join(map(lambda x: ord(x) ^ random.randint(1, 128), string_in)))
          

def digest_str(string_in):
    return skein1024(bytes(string_in, 'ascii')).hexdigest()

def compare(string_in):
     diff_bits = 0
     for i, char in enumerate(string_in):
         if char == target[i]:
             diff_bits += 1
     return diff_bits

def write_to_file(idnum, string_out):
    outfile = open(str(idnum) + '_core_record.txt', 'w')
    outfile.write(string_out)
    outfile.close()
    
if __name__ == "__main__":
    main()
