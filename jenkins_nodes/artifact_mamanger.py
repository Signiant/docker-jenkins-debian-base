import os
import re
import collections
import shutil
import traceback
from os.path import join
from xml.dom import minidom

print("Start")
a = []
rpt = []
Folders = []
Address = []

def list_duplicates(seq):
    global t
    t = False
    seen = set()
    seen_add = seen.add
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    b = ' \n'.join(seen_twice)
    e = len(seen_twice)
    if e >= 0:
        t = True
        fo = open("duplicates.txt", "w")
        fo.write(b)
        fo.close();
  
    return t

def fetch_buildnumbers(address):

    try:

        Id = 1
        for item in os.listdir(address):
            if 'Build-' in item:
                item_value= str(item)
                buildid, buildnumber=item_value.split("-", 1)
                Folders.append(buildnumber)
                Id += 1         
        return Folders
    except:
        print("___________________________ ERROR ___________________________\n" + traceback.format_exc())

def delete_releases(project, family, branch, buildnumber, jenkins):
    global path1
    path1= str('/var/lib/jenkins/jobs/'+ jenkins + '/builds/' + buildnumber)
    print(path1);
    global path2
    path2= str('/Releases/Jenkins/' + family + '/' + project + '/' + branch + '/Build-' + buildnumber) 
    try:
        path1_exists=os.path.exists(path1) 
        path2_exists=os.path.exists(path2)
     
        if path1_exists == False and path2_exists == True:
            shutil.rmtree(path2)
            print("Deleting artifacts : " + path2)

        return path2
    except:
        print("___________________________ ERROR ___________________________\n" + traceback.format_exc())

def start():
    try:
        fo.write("*********  Step 1 - Find All Jenkins Plan duplicate configurations **********\n")

        for (dirname, dirs, files) in os.walk('/var/lib/jenkins/jobs'):
            for filename in files:
                if filename.endswith('config.xml') :
                    thefile = os.path.join(dirname,filename)
                    get_jenkins = thefile
                    path_list = get_jenkins.split(os.sep)
                    # print(path_list);
                    print_filename=str(thefile)
                    if 'configurations' in print_filename or 'promotions' in print_filename:
                        donothing = 1
                    else:
                        fo.write("Adding Metadata from : " + print_filename )
                        xmldoc = minidom.parse(thefile)
                        projectlist = xmldoc.getElementsByTagName('project')
                        matrixlist = xmldoc.getElementsByTagName('matrix-project')
                        tagnumToKeep = xmldoc.getElementsByTagName('numToKeep')
                        if tagnumToKeep is not None and tagnumToKeep.length == 1:
                            numToKeep = int(tagnumToKeep[0].childNodes[0].data)
                            fo.write("Number to keep :" + tagnumToKeep[0].childNodes[0].data + "\n")
               
                        EnvInjectJobProperty = xmldoc.getElementsByTagName('EnvInjectJobProperty')
                        d = EnvInjectJobProperty.length
                        fo.write("EnvInjectJobProperty ;" + str(d) + "\n")

                        if EnvInjectJobProperty is not None and d == 1:
                            propertiesContent = xmldoc.getElementsByTagName('propertiesContent')[0]

                            name = propertiesContent.childNodes[0].data

                            fo.write("propertiesContent :" + name + "\n")
                            m = re.match("(?P<project_branch>\w+)\W+(?P<branch>\w+)\W+(?P<project_family>\w+)\W+(?P<family>\w+)\W+(?P<project_title>\w+)\W+(?P<title>\w+)", name)
                        
                    
                            SigniantConfig = xmldoc.getElementsByTagName('org.jenkinsci.plugins.variablecfg.Signiant')
                           
                            if SigniantConfig.length == 1:
                                artmanager=(SigniantConfig[0].childNodes[1].childNodes[0].data)
                            else:
                                artmanager="skip"

                            fo.write("Art Manager :" + artmanager + "\n")
                            if 'skip' in artmanager:
                                donothing = 1
                                str_report=("*** Record Skipped " + path_list[5])
                                rpt.insert(0, str_report)
                                fo.write("Art Manager said to skip record\n")
                                fo.write("*******************************************************************************\n")
                            else:
                                if m is None:
                                   donothing = 1
                                   fo.write("re match was None\n")
                                   fo.write("*******************************************************************************\n")
                                else:
                                    str_print = str(m.group("project_branch")+"="+ m.group("branch")+"  "+ m.group("project_family")+"="+m.group("family")+"  "+m.group("project_title")+"="+m.group("title")) 
                                    str_projectlist=str(m.group("title") + "=" + m.group("branch"))
                                    str_address=(m.group("family") + "/" + m.group("title") + "/" + m.group("branch") + "/" + path_list[5] )
                                    a.insert(0, str_projectlist) 
                                    
                                    str_report=(path_list[5] + "=" + m.group("title") + "-" + m.group("branch"))
                                    rpt.insert(0, str_report)
                                    
                                    Address.insert(0, str_address)
                                    fo.write("Match Data :" + str_print + "\n")
                                    fo.write("Address : " + str_address + "\n")
                                    fo.write("add to project list\n")
                                    fo.write("*******************************************************************************\n")
        return a                            
    except:
        print("___________________________ ERROR ___________________________\n" + traceback.format_exc())     


fo = open("runner.log", "w")
start()
fo.close();   


fo = open("Artifact_Manager.rpt", "w")
c = ' \n'.join(rpt)
fo.write(c)
fo.close();


# Checking for duplicates  
list_duplicates(a)
print(t);
if t == True:
    for address in Address: 
        family, project, branch, jenkins = address.split('/')
        search_address = str('/Releases/Jenkins/' + family + '/' + project + '/' + branch)
        
        # print(str('/Releases/Jenkins/' + address));
        # family, project, branch= address.split('/')
        # check if releases directory exists 
        if os.path.exists(search_address) == True:
            del Folders[:]
            # fetch the builds numbers for this project
            fetch_buildnumbers(search_address)
            # now delete the releases directory's
            for buildnumber in Folders:
                delete_releases(project, family, branch, buildnumber, jenkins)
else:
    print("** Duplicates found no builds will be delete until they have been corrected")

print("Done")

