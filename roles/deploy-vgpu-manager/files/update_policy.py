#!/usr/bin/env python3

import openshift as oc
from json import loads, dumps
from base64 import b64decode
from os import path 
from os  import environ as env
import argparse


def getPodsNamespace(KUBECONFIG: str) -> list:
    with oc.api_server(kubeconfig_path=KUBECONFIG), oc.project(getNamespace()):
        return oc.selector('pods').objects() 

def getPodsDefinition(data: list, pod_name: str) -> dict:
    for pod_obj in data:
        if pod_name in pod_obj.name():
           return pod_obj.model

def getNvidiaExamplePolicy(KUBECONFIG: str) -> dict:
    with oc.api_server(kubeconfig_path=KUBECONFIG), oc.project(getNamespace()):
        obj = oc.selector('ClusterServiceVersion').objects()
    for csv_obj in obj:
        if "gpu-operator-certified" in csv_obj.name():
           return loads(csv_obj.model.metadata.annotations["alm-examples"])[0]

def patchUpdateWithPolicy(policy: dict, update: dict) -> dict:
    for key in update["spec"]:
        policy["spec"][key] = update["spec"][key]
    return dumps(policy, indent=2)

def verifyUpdateFile(data: str) -> dict:
    try:
        return eval(b64decode(data))
    except:
        print("ERROR: Invalid json.  required: json base64 encoded")
        exit(1)

def applyJsontoOpnshift(KUBECONFIG: str, file: dict) -> bool:
        with oc.api_server(kubeconfig_path=KUBECONFIG):
            oc.apply(file)
        return True

def getCurrentPolicy(KUBECONFIG: str) -> dict:
     with oc.api_server(kubeconfig_path=KUBECONFIG):
        obj = oc.selector('ClusterPolicy').objects()
        if not len(obj) == 0:
            for policy_obj in obj:
                print(policy_obj.as_json())
        else:
            print("ERROR: Couldn't find policy")
            exit(1)

def GetkubeConfig() -> str:
    if path.exists(args.kubeconfig):
        return args.kubeconfig
    else:
        print("ERROR: couldn't locate KUBECONFIG path")
        exit(1)

def getNamespace() -> str:
    if "NAMESPACE" in env:
        return env.get("NAMESPACE")
    else:
        return "nvidia-gpu-operator"


parser = argparse.ArgumentParser(description = 'update nvidia operator policy')
subparser = parser.add_subparsers(metavar='', dest='command')

KUBECONFIG_DESCRIPTION = "KUBECONFIG path, default using enviorment 'KUBECONFIG'"

### get  
get = subparser.add_parser("get", help="Print Infomation")
get_subparser = get.add_subparsers(metavar='', dest='get')

get_default_policy = get_subparser.add_parser("default", help="Print default policy")
get_default_policy.add_argument('-k', '--kubeconfig', default=env.get('KUBECONFIG'),help=KUBECONFIG_DESCRIPTION)

get_rendered_policy = get_subparser.add_parser("render", help="Print rendered policy")
get_rendered_policy.add_argument('-k', '--kubeconfig', default=env.get('KUBECONFIG'),help=KUBECONFIG_DESCRIPTION)
get_rendered_policy.add_argument('-u','--use-current',default=False, required=False, help="Use current policy instead of default policy, default 'False'")
get_rendered_policy.add_argument('-p','--patch',type=str, required=True, help="json encoded base64 to patch")


get_current_policy = get_subparser.add_parser("current", help="Print configured policy")
get_current_policy.add_argument('-k', '--kubeconfig', default=env.get('KUBECONFIG'),help=KUBECONFIG_DESCRIPTION)


### set
set = subparser.add_parser("set", help="set configuration Infomation")
set_subparser = set.add_subparsers(metavar='', dest='set')

set_default_policy = set_subparser.add_parser("default", help="apply using default policy")
set_default_policy.add_argument('-k', '--kubeconfig', default=env.get('KUBECONFIG'),help=KUBECONFIG_DESCRIPTION)

set_rendered_policy = set_subparser.add_parser("render", help="apply renderd policy")
set_rendered_policy.add_argument('-k', '--kubeconfig', default=env.get('KUBECONFIG'),help=KUBECONFIG_DESCRIPTION)
set_rendered_policy.add_argument('-u','--use-current',default=False, required=False, help="Use current policy instead of default policy, default 'False'")
set_rendered_policy.add_argument('-p','--patch',type=str, required=True, help="json encoded base64 to patch")


args = parser.parse_args()



if args.command == "get":
    match args.get:
        case "default":
            print(dumps(getNvidiaExamplePolicy(KUBECONFIG=GetkubeConfig()), indent=2 ))
        case "render":
            if args.use_current:
                policy = getCurrentPolicy(KUBECONFIG=GetkubeConfig())
            else:
               policy = getNvidiaExamplePolicy(KUBECONFIG=GetkubeConfig())
            print(patchUpdateWithPolicy(policy=policy, update=verifyUpdateFile(args.patch)))
        case "current":
            getCurrentPolicy(KUBECONFIG=GetkubeConfig())
        case _:
            get.print_help()
            exit(1)

elif args.command == "set":
    match args.set:
        case "default":
            default_policy = getNvidiaExamplePolicy(KUBECONFIG=GetkubeConfig())
            applyJsontoOpnshift(KUBECONFIG=GetkubeConfig(), file=default_policy)
        case "render":
            if args.use_current:
                policy = getCurrentPolicy(KUBECONFIG=GetkubeConfig())
            else:
               policy = getNvidiaExamplePolicy(KUBECONFIG=GetkubeConfig())
            renderd_policy = patchUpdateWithPolicy(policy=policy, update=verifyUpdateFile(args.patch))
            if applyJsontoOpnshift(KUBECONFIG=GetkubeConfig(), file=renderd_policy):
                print(renderd_policy)
        case _:    
            set.print_help()
            exit(1)
else:
    parser.print_help()
    exit(1)
