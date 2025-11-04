import argparse
import os


def get_args():
    parser = argparse.ArgumentParser(prog='AFG',
                                     description='examples files configuration')
    parser.add_argument('--home_path', type=str,
                        default=os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))
    parser.add_argument('--dataset_dir', type=str,default='examples/eai_vr_home')
    parser.add_argument('--action_pred', type=str,default='eai_vrhome_actions.json')
    parser.add_argument('--env_file', type=str,default='file3_1.json')
    parser.add_argument('--object_name',default=['character']) # objects in graph
    return parser.parse_args()