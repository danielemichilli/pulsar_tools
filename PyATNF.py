"""Query ATNF pulsar catolog."""
import urllib2
import urllib, sys, re, commands
from tools.html2plaintext import *



def _retrieve(line, keylist, pattern):
    def KeyListGen(keylist):
        for key in keylist:
            yield key
    KG = KeyListGen(keylist)
    results = {}
    for match in pattern.finditer(line):
        value = str(match.group('value'))
        #print 'value: ', value
        if value == '*' or value == 'NONE': value = None
        uncertainty = str(match.group('uncertainty')).replace('(','').replace(')','')
        if uncertainty == '*' or uncertainty == 'NONE' or uncertainty == 'None':uncertainty = None
        #print 'uncertainty: ', uncertainty
        try: 
            #match.group('ref'):
            ref = str(match.group('ref'))
            if ref == '*' or ref == 'NONE' or ref == 'None':ref = None
            #print 'ref: ', ref
            results[KG.next()] = (value, uncertainty, ref)
        except:
            results[KG.next()] = (value, uncertainty)
    return results

def LQatnf(psr, Query=('RaJ', 'DecJ')):
    if psr == 'all':psr=''
    keylist = list(Query)
    Nkey = len(keylist)
    text = commands.getoutput('''psrcat -c "%(keylist)s" %(pulsar)s ''' % {'pulsar':psr, 'keylist':' '.join(keylist)})
    #print text
    p = re.compile('(?P<Number>\d+)(?P<line>(\s+(?P<value>-*\+*(\d{2,2}\:)*(\d+\.*\d*(e-*\+*\d+)*)|\*|([JB]\d{4}[-\+]\d{2,4}))(\s+(?P<uncertainty>\d{1,2}))*(?P<ref>\s+[a-z]+\+*\d+\s*|\s*\[\d+\]\s*)*\s*){1,%d})\n' % (Nkey), re.U)
    pattern = re.compile('\s+(?P<value>(-*\+*(\d{2,2}\:)*\d+\.*\d*(e-*\+*\d+)*)|\*|([JB]\d{4}[-\+]\d{2,4}))(\s+(?P<uncertainty>\d{1,2})\s+){0,1}(\s+(?P<ref>[a-z]+\+{0,1}\d+|\[\d+\]))*')
    #finally:
    if psr == '':
        results = []
        for m in p.finditer(text):
            line = str(m.group('line'))
            #print m.group()
            #print 'line %s: \n%s' % (m.group('Number'),line)
            results.append(_retrieve(line, keylist, pattern))
        return results
    else:
        m = p.search(text)
        line = str(m.group('line'))
        #print 'line: \n',line
        results = _retrieve(line, keylist, pattern)
        return results

def Qatnf(psr, Query=('RaJ', 'DecJ')):
    if psr == 'all':psr=''
    name = psr.split()
    if len(name) == 2:
        if name[0] == 'PSR':
            psr = name[1]
    try:
    #for i in [1]:
        #Try query the webserver
        url = 'http://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php'
        data = {}
        if isinstance(Query, (basestring)):
            Query = [Query]
        for Q in Query:
            data[Q]=Q
        url_values = urllib.urlencode(data)
        data = {'ephemeris':'short', 'startUserDefined':'true','style':'Publication quality','sort_attr':'jname','sort_order':'asc'}
        url_values += '&'+urllib.urlencode(data)
        data = {'pulsar_names':psr}
        url_values += '&'+urllib.urlencode(data)
        data = {'x_axis':'','x_scale':'linear','y_axis':'','y_scale':'linear', 
            'no_value':'None','coords_unit':'raj/decj','radius':'','coords_1':'',
            'coords_2':'','fsize':'3' }
        url_values += '&'+urllib.urlencode(data)
        data = {'state':'query'}
        url_values += '&'+urllib.urlencode(data)
        data = {'table_bottom.x':'100', 'table_bottom.y':'100'}
        url_values += '&'+urllib.urlencode(data)
        full_url = url + '?' + url_values
        order = []
        for key in Query:
            idx = url_values.find(key)
            order.append((idx, key))
        order.sort()
        keylist = [x[1] for x in order]
        the_page = urllib2.urlopen(full_url).read()
        text = html2plaintext(the_page, encoding='UTF-8')
        #print text
        Nkey = len(keylist)
        #print Nkey
        #p = re.compile('(?P<Number>[ \t\n\r\f\v]\d+|\d+)(?P<line>(\s+(?P<value>-*\+*(\d{2,2}\:)*(\d+\.*\d*(e-*\+*\d+)*)|NONE|[JB]\d{4}[-\+]\d{2,4})(\s+(?P<uncertainty>\(\d{1,2}\))){0,1}(\s+(?P<ref>[a-z]+\+*\d{2}|\[\d+\]))*){1,%d})' % (Nkey), re.U)
        p = re.compile('(?P<Number>\d+)(?P<line>(\s+(?P<value>-*\+*(\d{2,2}\:)*(\d+\.*\d*(e-*\+*\d+)*)|NONE|([JB]\d{4}[-\+]\d{2,4}))(\s+(?P<uncertainty>\(\d{1,2}\))){0,1}(\s+(?P<ref>[a-z]+\+*\d+|\[\d+\]))*){1,%d})' % (Nkey), re.U)
        pattern = re.compile('(?P<number>(?P<value>-*\+*(\d{2,2}\:)*\d+(\.\d+){0,1}(e-*\+*\d+){0,1}|NONE|[JB]\d{4}[-\+]\d{2,4})(\s+(?P<uncertainty>\(\d{1,2}\))){0,1}(\s+(?P<ref>[a-z]+\+{0,1}\d+|\[\d+\]))*)')

        #finally:
        if not psr == '':
            m = p.search(text)
            line = m.group('line')
            #print 'line: \n',line
            results = _retrieve(line, keylist, pattern)
            return results
        else:
            results = []
            for m in p.finditer(text):
                line = m.group('line')
                #print m.group()
                #print 'line %s: \n%s' % (m.group('Number'),line)
                results.append(_retrieve(line, keylist, pattern))
            return results

    except:
        print 'web server query failed, try local database.\n'
        return LQatnf(psr, Query)


from Coordinate import RA, Dec

def QatnfPos(psr):
    info = Qatnf(psr)
    ra = RA(info['RaJ']).in_unit_degree
    dec = Dec(info['DecJ']).in_unit_degree
    return ra, dec


