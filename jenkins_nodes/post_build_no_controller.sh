#!/bin/bash

pass_JOB_NAME=$1

ls -td /var/lib/jenkins/workspace/$pass_JOB_NAME/* | awk "NR>1" | xargs rm -rf
