redmine2confluence-wiki
=======================

Set of scripts to import data from redmine wiki to Confluence
Based on:
- Tim Jansen's gist https://gist.github.com/tim-jansen/6263586 
- Stefan Bühler's redmine export script: http://stbuehler.de/blog/article/2011/06/04/exporting_redmine_wiki_pages.html

Usage:
----------
To use this conversion:
1. Execute ExportWiki.export_all from exportwiki.rb in the redmine environment. This will create set of folders with all the project data
2. Edit redmine_spaces.py file to 
	2.1. provide reference to Jira ticket link conversion or another ticketing system (it will replace \g<1> with original redmine ID)
	2.2. configure mapping of redmine projects to confluence spaces. Different projects can be mapped to the same space. in this case conflicting pages will be ignored
3. Modify 'import_confluence.py' to configure:
	- user name
	- password
	- confluence URL
4. Run the python script 'import_confluence.py' in the exported data folder (root level)

