import sys
import os
import re
import xmlrpclib
import mimetypes
from xmlrpclib import ServerProxy, Fault
# redmine data processing functions
import redmine
# we need a list of redmine spaces for reference
from redmine_spaces import spaces

# Connects to confluence server with username and password
site_URL = "https://your.confluence.site/"
server = ServerProxy(site_URL + "/rpc/xmlrpc")

username = "user"
pwd = "password"
token = server.confluence2.login(username, pwd)

def save_attachments(space, filename, curpage):
    # filename here is the full path
    for somedir, somesubdir, afiles in os.walk(filename[:-8]+'/'):
        #print "Attachments ", somedir, somesubdir, afiles
        for attachmentfile in afiles:
            with open(filename[:-8]+'/' + attachmentfile, 'rb') as f:
                    data = f.read(); # slurp all the data
            attachment = {};
            attachment['fileName'] = os.path.basename(attachmentfile);
            contentType = mimetypes.guess_type( attachmentfile )[0]
            if contentType:
                attachment['contentType'] = contentType;
            else:
                attachment['contentType'] = 'application/octet-stream';
            print attachment, " p=", curpage['id']
            try:
                server.confluence2.addAttachment(token, curpage['id'], attachment, xmlrpclib.Binary(data));
            except:
                # I have no idea which exception this thing throws, so all of them.
                print "ERROR: Can not upload file '{0}' for the page '{1}' in space {2}".format(filename[:-8]+'/' + attachmentfile, curpage['title'], space)




def save(space, filename, pagename):
    # Retrives text from a file and converts it
    content = redmine.wiki_to_confluence(filename)
    # Create empty page with content
    content = server.confluence2.convertWikiToStorageFormat(token, content)
    newpage = {"title":pagename, "space":space, "content":content}
    server.confluence2.storePage(token, newpage)
    # Push attachments to the page
    curpage = server.confluence2.getPage(token,space,pagename)
    save_attachments(space, filename, curpage)



for project_dir, subdirs, files in os.walk('.'):
    try:
        project_name = project_dir.split('/')[1]
    except IndexError:
        continue
    for filename in files:
        if filename[-8:] == '.textile':
            pagename = filename[:-8].replace('_',' ').strip()
            # If page name is 'Wiki' it needs to be changed in order to avoid conflicts 
            if pagename == 'Wiki':
                pagename = project_name + ' Wiki'
        else:
            continue
        try:
            server.confluence2.getPage(token,spaces[project_name],pagename)
        except KeyError:
            print "Project %s not mapped" % project_name
            break
        except Fault:
            pass
        else:
            print "Page %s exists" % pagename
            continue
        print "Saving page %s"% pagename
        save(spaces[project_name], os.path.join(project_dir,filename),pagename)

server.confluence2.logout(token)
