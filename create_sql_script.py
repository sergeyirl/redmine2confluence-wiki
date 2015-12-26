# produce .sql script that will be executed on the server
# the purpose is to change the author name of the wiki page

import os
import sys

from redmine_spaces import spaces, parent_pages, replace_page, redmine_confluence_user

sql_script = open ('fix-author.sql', 'w')

def	save(space, project_dir, filename, pagename):
    f = open (os.path.join(project_dir, filename))
    redmine_user = f.read().split()[0][1:-1]
    confluence_user = redmine_confluence_user[redmine_user]
    f.close()
    sql_statement = """
update content set creator = (select user_key from user_mapping where lower_username = '{0}')
 where contentid in (select c2.contentid from content c2 where c2.title = '{1}'
                     and spaceid = (select spaceid from spaces where spacekey = '{2}'));
""".format(confluence_user, pagename, space)
    sql_script.write(sql_statement)

for project_dir, subdirs, files in os.walk('.'):
    try:
        project_name = project_dir.split('/')[1]
    except IndexError:
        continue
    if project_name != "myscript-resources":
        continue
    for filename in files:
        if filename[-11:] == '.extra-info':
            pagename = filename[:-11].replace('_',' ').strip()
            # If page name is 'Wiki' it needs to be changed in order to avoid conflicts
            if pagename == 'Wiki':
                pagename = project_name + ' Wiki'
            # Fix page that had weird character such as / or ?.
            if pagename in replace_page:
                pagename = replace_page[pagename]
        else:
            continue
	save(spaces[project_name], project_dir ,filename, pagename)

sql_script.close()

# vim:et:sw=4:ts=4:

