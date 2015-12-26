redmine2confluence-wiki
=======================

Set of scripts to import data from redmine wiki to Confluence
Based on:
- Tim Jansen's gist https://gist.github.com/tim-jansen/6263586 
- Stefan Bühler's redmine export script: http://stbuehler.de/blog/article/2011/06/04/exporting_redmine_wiki_pages.html

Usage:
----------
To use this conversion:
- Execute ExportWiki.export_all from exportwiki.rb in the redmine environment. This will create set of folders with all the project data
- Edit redmine_spaces.py file to 
	* provide reference to Jira ticket link conversion or another ticketing system (it will replace \g<1> with original redmine ID)
	* configure mapping of redmine projects to confluence spaces. Different projects can be mapped to the same space. in this case conflicting pages will be ignored
- Modify 'import_confluence.py' to configure:
	* user name
	* password
	* confluence URL
- Run the python script 'import_confluence.py' in the exported data folder (root level)

Examples 1:
---------

Exporting a single project by name from Redmine 2 / Rails 3:

    $ cd /PATH/TO/redmine
    $ script/rails console production
    > require("/PATH/TO/redmine2confluence-wiki/export_wiki.rb")
    > ExportWiki.export_wiki("/tmp", Project.find_by_name("PROJECT NAME").wiki)

Example 2:
---------

This is how we used it with Redmine 2.2.0, Ruby 1.8.7 and Rails 3.2.9.

First I had to find the rails command:

    # find / -name rails

Next execute the script:

    # cd /PATH/TO/redmine
    # RAILS_ENV=production /var/lib/gems/1.8/bin/rails console
    > load "exportwiki.rb"
    > ExportWiki.export_all()

All the pages will be saved under /tmp/redmine.

Move the page to the location of the script.

    # mv /tmp/* .

Next I tried with a test Confluence server. Some pages might be refused by Confluence. I split the file in two till I find the line that causes the problem. Put the line in redmine_space.py.

I also created a script that generates a SQL script to be run by Postgresql to fix page authors. The process is described here:

https://confluence.atlassian.com/display/CONFKB/How+to+change+the+creator+of+a+page

    # ./create_sql_script.py

This will result in a script called 'fix-author.sql' to be run on the Confluence server.
