import logging
import os
import sys
import argparse
import time

from datetime import datetime

MY_FILE_NAME='output_{}.txt'.format(datetime.now().strftime("%Y%m%d%H%M%S"))
MY_FILE_CONTENT='Hello vertex AI'  #@param {type:"string"}

def main(args):
  # WRITE YOUR TRAINING CODE HERE
  # For now we just write a file to the NFS and verify the file exists here

  assert (os.path.exists(args.mount_root_path)),"Mounted Path Not Found"
  print("Files in folder {} are:\n".format(args.mount_root_path))
  print(os.listdir(args.mount_root_path))

  output_dir = os.path.join(args.mount_root_path, args.subfolder)
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  print("Files in folder {} are:\n".format(output_dir))
  print(os.listdir(output_dir))

  output_file = os.path.join(
      output_dir,
      MY_FILE_NAME)
  print("Writing a new file {} to the folder... \n".format(output_file))
  f = open(output_file, "w")


  f.write(MY_FILE_CONTENT)
  f.close()

  print("Files in folder {} are:\n".format(output_dir))
  print(os.listdir(output_dir))

  sys.exit(0)

if __name__ == "__main__":
  logging.getLogger().setLevel(logging.INFO)
  PARSER = argparse.ArgumentParser()
  # Input Arguments
  PARSER.add_argument(
      '--mount_root_path',
      help='The path in worker where NFS is mount to',
      default='/mnt/nfs/data')
  PARSER.add_argument(
      '--subfolder',
      help='The subfolder under the mount path for writing files',
      default='public')
  PARSER.add_argument(
      '--sleep_time',
      help='Sleep time',
      default=120)
  
  ARGUMENTS, _ = PARSER.parse_known_args()

  main(ARGUMENTS)