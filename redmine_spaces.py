# -*- coding: utf-8 -*-
#spaces = {  "foo":"NLP" }
#parent_pages = { "foo": "12058669" }  # set page id, can find id by https://confluence.atlassian.com/display/CONFKB/How+to+Get+Confluence+Page+ID+From+The+User+Interface
spaces = {  "test":"TEST" }
parent_pages = { "test": "11111111" }  # set page id, can find id by https://confluence.atlassian.com/display/CONFKB/How+to+Get+Confluence+Page+ID+From+The+User+Interface

jira_url="{jiraissues:url=https://your.jira.url/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=%22External+issue+ID%22+%7E+\g<1>&tempMax=10|columns=key,summary,status}"

# slash can't be represented in Linux file so handle them here
replace_page = {
'CR réunion 0108' : 'CR réunion 01/08',
'CR réunion 0509' : 'CR réunion 05/09',
}

# dictionary to fix troublesome lines. You will need to split up your textile file in two till you find the line Confluence does not accept.
fixup_line = {
'* Check if a *tokenized\_SHA1\* matches _*tokenizerDir*_ SHA1\r' :
'* Check if a *tokenized\_SHA1* matches _*tokenizerDir*_ SHA1\r',
'* You can list (*--File*) as you wish.' :
'* You can list (*\-\-File*) as you wish.'}

# dictionary mapping Redmine user to Confluence user
redmine_confluence_user = {
'ivan' : 'ivan.kanis',
'joe' : 'joe.smith'}
