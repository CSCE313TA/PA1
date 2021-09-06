#!/usr/bin/python3
import random
from subprocess import run, call, Popen, PIPE, check_output
import subprocess
import sys
import glob
from time import sleep
import os
import filecmp


SHOULD_SPAWN_SERVER = False

def randrange_float(start, stop, step):
    return round(random.randint(0, int((stop - start) / step)) * step + start, 3)

def setup():
	if SHOULD_SPAWN_SERVER:
		os.system("./server &")

def cleanup():
	os.system("killall server")
	fifo_files = glob.glob("fifo*")
	if len(fifo_files) > 0:
		for i in fifo_files:
			os.remove(i)
		return False
	else:
		return True

def request_datapoint(time, ecg, person):
	p = Popen(["./client", "-p" , str(person), "-e", str(ecg), "-t", str(time)], stdout=PIPE, stdin=None)
	output = p.stdout.readline().decode()
	p.terminate()
	with open(f"BIMDC/{person}.csv","r") as f:
		try:
			return next(x for x in f.readlines() if x.split(",")[0] == str(time)).split(",")[ecg] in output
		except:
			return False


def request_random_datapoint():
	time = randrange_float(0,49.996, 0.004)
	ecg = random.randint(1,2)
	person = random.randint(1,15)
	setup()
	ret = request_datapoint(time, ecg, person)
	sleep(0.2)
	cleanup()
	return ret


def check_file_csv():
	p = Popen(["./client", "-f", "1.csv"], stdout=PIPE, stdin=None)
	sleep(0.5) # this is a hack but we can't do better without knowledge that the server will close itself
	return filecmp.cmp("BIMDC/1.csv", "received/1.csv")

def check_file_binary():
	with open('BIMDC/rand.bin', 'wb') as out:
		out.write(os.urandom(1024))
	p = Popen(["./client", "-f", "rand.bin"], stdout=PIPE, stdin=None)
	sleep(0.5) # this is a hack but we can't do better without knowledge that the server will close itself
	return filecmp.cmp("BIMDC/rand.bin", "received/rand.bin")

def try_child():
	p = Popen(["./client", "-p" , "1", "-e", "1", "-t", "0"], stdout=PIPE, stdin=None)
	sleep(0.5)
	return not any([b"server" in x.split()[3] for x in check_output(["ps"]).split(b"\n") if len(x) > 3])


earned_points = 0
sum_points = 0

cleanup()
SHOULD_SPAWN_SERVER = try_child()

if "CHILD" in sys.argv:
	sum_points += 15
	if not SHOULD_SPAWN_SERVER:
		earned_points += 15

if "DATAPOINT" in sys.argv:
	sum_points += 15
	check = all([request_random_datapoint() for x in range(5)])
	if check:
		earned_points += 15

if "FILE_CSV" in sys.argv:
	sum_points += 20
	if check_file_csv():
		earned_points += 20

if "FILE_BINARY" in sys.argv:
	sum_points += 10
	if check_file_binary():
		earned_points += 10

clean = cleanup()

if "CLEANUP" in sys.argv:
	sum_points += 5
	if clean:
		earned_points += 5


print(f"{earned_points}/{sum_points} points for cases {sys.argv[1:]}")
if sum_points == earned_points:
	exit(0)
else:
	exit(1)