import sys
import os
import re
# we need a list of redmine spaces for reference
from redmine_spaces import spaces, jira_url, fixup_line

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
    if text and text != article:
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
        reference = macro.group(0)
    print reference
    # {{include(reference)}} => {include:reference}
    reference = re.search('\((.*)\)', reference ).group(1)
    print reference
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
    # (<pre> block) -> noformat
    content = re.sub('(?s)<pre>(.*?)</pre>','{noformat}\g<1>{noformat}',content)
    # Redmine issue ID converted to Jira
    content = re.sub('\s#([0-9]+)', jira_url, content )
    # remove the rest of redmine macro. include them as comments. Someone can filter/replace them later
    content = re.sub("(?s){{(.*)}}", 'redmine_macro:{{\g<1>}}', content)
    return content

def bold_match (match):
    """Shield underscore within bold"""
    part = match.group(1)
    part = re.sub(r'_', '\_', part)
    return '*' + part + '*'

def shield_bold_line (line):
    """Shield bold within line"""
    line = re.sub(r'\*(.*?)\*', bold_match, line)
    return line

def horizontal_rule(line):
    """Any line with more than 4 hyphens is treated as a horizontal rule"""
    strip_line = line.rstrip('\r')
    if len(strip_line) >= 4 and re.search(r'^-+$', strip_line):
        # confluence horizontal line
        line = '----'
        # tack carriage return if there was one
        if line[len(line) -1] == '\r':
            line += '\r' 
    return line

def process_effect (line):
    # protect hyphen with unicode hyphen
    line = re.sub('^- ', u'\u2010 '.encode('utf8'), line)
    # blockquote
    return re.sub('^> ', 'bq. ', line)
    
def process_star (line):
    leading_star = re.compile(r'(^\*+ )(.*)')
    match = re.search(leading_star, line)
    if match and len(match.groups()) == 2:
        # process stars minus the one in front of the line
        line = match.group(1) + shield_bold_line (match.group(2))
    else:
        line = shield_bold_line(line)
    return line

def shield_monospace (match):
    """Shield hyphen and star within monospace"""
    part = match.group(1)
    part = re.sub(r'\*', '\*', part) 
    part = re.sub('-', '\-', part) 
    return '{{' + part + '}}'

def process_monospace (line): 
    return re.sub('@(.*?)@', shield_monospace, line)

def shield_italic (match):
    """Shield star and hyphen within italic"""
    part = match.group(1)
    part = re.sub(r'\*', '\*', part) 
    part = re.sub('-', '\-', part) 
    return '_' + part + '_'

def process_italic (line):
    return re.sub('_(.*?)_', shield_italic, line)

def process_line_by_line (content):
    """Process content line by line"""
    output = ""
    verbatim = False

    for line in content.split('\n'):
        # don't process lines within <pre> </pre>
        if verbatim:
            if re.search('</pre>', line):
                verbatim = False
        else:
            if re.search('<pre>', line):
                verbatim = True
            else:
                line = process_star(line)
                line = process_monospace(line)
                line = process_italic(line)
                line = process_link(line)
                line = process_effect(line)
                line = horizontal_rule(line)
        output += line + '\n'
    return output

def process_link(line):
    single_bracket = False
    double_bracket = False
    parse = [] 
    part = ''
    previous_character = ''

    for character in line:
        if character == '[':
            if single_bracket:
                if previous_character == '[':
                    double_bracket = True
            else:
                single_bracket = True
            parse.append({part : 'normal'})
            part = ''
        elif character == ']':
            if double_bracket:
                if previous_character == ']':
                    double_bracket = False
                    parse.append({part : 'double-bracket'})
                    part = ''
            else:
                single_bracket = False
                parse.append({part : 'single-bracket'})
                part = ''
        else:
            part += character 
        previous_character = character
    if part != '':
        parse.append({part : 'normal'})

    output = ''
    for part in parse:
        for key in part:
            if part[key] == 'normal':
                output += key
            elif part[key] == 'single-bracket':
                if re.search('^http(s?):', key):
                    output += '[' + key + ']'
                else:
                    # protect bracket with double width bracket
                    output += u'\uff3b'.encode('utf8') + key + u'\uff3d'.encode('utf8')
            elif part[key] == 'double-bracket':
                output += '[[' + key + ']]'
            else:
                raise NameError('Something is wrong')

    return output

def line_fixup (content):
    """Fix border line cases"""
    output = ""

    for line in content.split('\n'):
        try:
            if fixup_line[line]:
                output += fixup_line[line]
            else:
                output += line
        except KeyError:
            output += line
        output += '\n'
    return output
            
def clean_attachment(match):
    """Clean content within textile attachment (markup !!)"""
    # discard path leading to attachment
    part = match.group(1).split('/')[-1] 
    # discard >, it indicate right floating image on Redmine
    part = re.sub('^>', '', part)
    # discard {}, used to specify pixel width for example 
    part = re.sub('{.*}', '', part)
    return '!' + part + '!'
    
def wiki_to_confluence(filename):
    """Load the redmine wiki page in Textile format and converts it to confluence markup. Returns content as a string."""
    # Retrives text from a file
    f = open(filename, 'r')
    content = f.read()
    f.close()

    # File text is loaded into memory, we can start converting it

    # clean attachments
    content = re.sub('!(.*?)\!', clean_attachment, content)

    # Things that need to be processed line by line
    content = process_line_by_line (content)

    # convert macro to confluence
    content = macro_to_confluence(content)
    # table conversions
    content = tables_to_confluence( content )

    # Now let's replace all the link references
    content = urls_to_confluence( content )
    # remove all the paragraph markup
    content = re.sub( '^\s*p[=<>]*((?s)\{[^\}]*\})*\.','', content )

    # final line fixup
    content = line_fixup(content)

    return content

# vim:et:sw=4:ts=4:

