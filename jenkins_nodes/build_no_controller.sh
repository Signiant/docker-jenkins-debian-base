#!/bin/bash

pass_JOB_NAME=$1
pass_LABEL=$2

ls -td /var/lib/jenkins/workspace/$pass_JOB_NAME/label/$pass_LABEL/* | awk "NR>1" | xargs rm -rf

