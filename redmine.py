import sys
import os
import re
# we need a list of redmine spaces for reference
from redmine_spaces import spaces, jira_url

MatchObject = type(re.search('', ''))

def wiki_reference_to_confluence(reference):
    """Converts single wiki reference from redmine format to Conflence markup and returns as a string."""
    # check if this is called from inside of regexp
    if isinstance(reference, MatchObject):
        reference = reference.group(0)
    # strip start and end brackets and whitespace
    reference = reference.strip('[]').strip()
    # split into text markup and reference: [text|reference] => [reference|text]. [reference] => [reference|reference]
    parts = reference.split('|')
    if len(parts) > 1:
        reference = parts[0]
        text = parts[1]
    else:
        reference = parts[0]
        text = reference
    # now we should do some magic on the reference
    # Get project name out of it
    parts = reference.split(':')
    if len(parts) > 1:
        reference = parts[1]
        project = parts[0]
        # look up the required space here.
        try:
            space = spaces[project]
        except KeyError:
            # if it is not mapped, we will just return the project reference
            space = project
    else:
        reference = parts[0]
        project = None
        space = None
    # Now let's see if it references an anchor
    parts = reference.split('#')
    if len(parts) > 1:
        anchor = parts[1]
        article = parts[0]
    else:
        article = parts[0]
        anchor = None
    # remove or replace bad symbols in the link
    article = article.replace('_',' ').replace('.', '')
    # now create reference back
    reference = article
    if space:
        reference = space + ':' + reference
    if anchor:
        reference = reference + '#' + anchor
    if text:
        reference = text + '|' + reference
    # debug printout
    # print 'space: \'{0}\', article: \'{1}\', anchor: \'{2}\', text: \'{3}\'\nOutput: [{4}]'.format(space, article, anchor, text, reference)
    # return the new reference
    return '[' + reference + ']'


def tables_to_confluence(content):
    """Convert tables from redmine format to confluence. Returns content as a string"""
    # Replace table header cells. We will discard left/right alignment.
    # TODO: make sure that we are ignoring insides of the code blocks (e.g. <pre>)
    # Split apart empty cells
    content = content.replace('||','| |')
    # Properly mark header cells
    content = re.sub('\|_[><=]*((?s)\{[^\}]*\})*\.','||',content)
    # Remove incompatible cell alignment
    content = re.sub('\|[><=]*((?s)\{[^\}]*\})*\.','|',content)
    return content


def urls_to_confluence(content):
    """Convert all the URL, attachment and wiki links from redmine format to confluence. Returns content as a string"""
    # replace all the internal wiki references
    content = re.sub('(?s)(\[\[[^\]]*\]\])', wiki_reference_to_confluence, content )
    # replace all the attachments code
    content = re.sub('attachment:(\S+)','[^\g<1>]', content)
    # replace links with quotes. "text":xxx://something => [text|xxx://something]
    content = re.sub('(?s)\"([^"]*)\":([a-zA-Z]+):(/?/?)(\S+)','[\g<1>|\g<2>:\g<3>\g<4>]', content)
    # replace links without quotes (probably). text:xxx://something => [text|xxx://something]
    content = re.sub('(\S+):([a-zA-Z]+):(/?/?)(\S+)','[\g<1>|\g<2>:\g<3>\g<4>]', content)
    return content


def include_macro(macro):
    """Helper function to convert {include} macro. Returns string"""
    if isinstance(macro, MatchObject):
        macro = reference.group(0)
    # {{include(reference)}} => {include:reference}
    reference = re.search('\(.*\)', macro ).group(0)
    # convert reference to the proper format and cut extra [] returned by the conversion function
    reference = wiki_reference_to_confluence(reference).strip('[]')
    return "{include:" + reference + "}"


def macro_to_confluence(content):
    """Convert macro content to confluence format and return as a string."""
    # shield all of the {} single instances. Confluence treats them as macro
    content = re.sub('([^\{])\{([^\{])', '\g<1>\{\g<2>', content)
    content = re.sub('([^\}])\}([^\}])', '\g<1>\}\g<2>', content)
    # table of contents {toc}
    content = re.sub('\{\{[><=]*toc\}\}','{toc}', content)
    # include wiki reference
    content = re.sub('(?s)({{\s*include\s*\(.*\)\s*}})',include_macro, content)
    # code (<pre> block)
    content = re.sub('(?s)<pre>(.*?)</pre>','{code}\g<1>{code}',content)
    # Redmine issue ID converted to Jira
    content = re.sub('\s#([0-9]+)', jira_url, content )
    # remove the rest of redmine macro. include them as comments. Someone can filter/replace them later
    content = re.sub("(?s){{(.*)}}", 'redmine_macro:{{\g<1>}}', content)
    return content



def wiki_to_confluence(filename):
    """Load the redmine wiki page in Textile format and converts it to confluence markup. Returns content as a string."""
    # Retrives text from a file
    f = open(filename, 'r')
    content = f.read()
    f.close()
    # File text is loaded into memory, we can start converting it
    # convert macro to confluence
    content = macro_to_confluence(content)
    # table conversions
    content = tables_to_confluence( content )
    # Now let's replace all the link references
    content = urls_to_confluence( content )
    # remove all the paragraph markup
    content = re.sub( '^\s*p[=<>]*((?s)\{[^\}]*\})*\.','', content )
    # convert inline monospace
    content = re.sub(r'@(.*?)@',r'{{\1}}',content)
    # TODO: The rest of the stuff. I'm too lazy and it does not seem to be too important
    return content
