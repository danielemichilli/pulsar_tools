import re

def SSprec(SS, error=9.):
    p = re.compile('\d+\.*(?P<digits>\d*)')
    m = p.search(SS)
    #print m.group('digits')
    return error*0.1**len(m.group('digits'))

class RA(object):
    def __init__(self, value):
        if isinstance(value, (tuple, list)):
            if value[1] == 'None':
                error = 9
            else:
                error = value[1]
            value = value[0]
            try:
                self.in_unit_degree = float(value)
                self.uncertainty = SSprec(value, error=float(error))
                hh = self.in_unit_degree/15
                self.HH = int(hh)
                mm = (hh % 1)*60
                self.MM = int(mm)
                self.SS = (mm % 1)*60
                self.SSuncertainty = self.uncertainty*60.*4.
            except:
                pattern = re.compile('(?P<HH>\d\d)[:\s](?P<MM>\d\d)[:\s](?P<SS>\d\d\.*\d*)')
                match = pattern.search(value)
                self.HH = int(match.group('HH'))
                self.MM = int(match.group('MM'))
                self.SS = float(match.group('SS'))
                self.SSuncertainty = SSprec(match.group('SS'), error=float(error))
                self.in_unit_degree = (self.HH+self.MM/60.+self.SS/60./60.)*15
                self.uncertainty = self.SSuncertainty/60./4.
                #print self.SSuncertainty
        elif isinstance(value, (basestring,float)):
            return RA.__init__(self, (value, 9))
class Dec(object):
    def __init__(self, value):
        if isinstance(value, (tuple, list)):
            if value[1] == 'None':
                error = 9
            else:
                error = value[1]
            value = value[0]
            try:
                self.in_unit_degree = float(value)
                self.uncertainty = SSprec(value, error=float(error))
                if self.in_unit_degree < 0.:
                    self.sign = '-'
                else:
                    self.sign = '+'
                dd = abs(self.in_unit_degree)
                self.dd = int(dd)
                mm = (dd % 1)*60
                self.mm = int(mm)
                self.ss = (mm % 1)*60
                self.SSuncertainty = self.uncertainty*60.*60
            except:
                pattern = re.compile('(?P<sign>-*\+*)(?P<dd>\d\d)[:\s](?P<mm>\d\d)[:\s](?P<ss>\d\d\.*\d*)')
                match = pattern.search(value)
                self.sign = str(match.group('sign'))
                self.dd = int(match.group('dd'))
                self.mm = int(match.group('mm'))
                self.ss = float(match.group('ss'))
                self.SSuncertainty = SSprec(match.group('ss'), error=float(error))
                if self.sign == '-':
                    self.in_unit_degree = -1.*(self.dd+self.mm/60.+self.ss/60./60.)
                else:
                    self.in_unit_degree = self.dd+self.mm/60.+self.ss/60./60.
                self.uncertainty = self.SSuncertainty/60./60.
                #print self.SSuncertainty
        elif isinstance(value, (basestring,float)):
            return Dec.__init__(self, (value, 9))


class coordinate(object):
    def __init__(self, values):
        ra,dec = values.split('  ')[:2]
        self.RA = RA(ra)
        self.Dec = Dec(dec)
